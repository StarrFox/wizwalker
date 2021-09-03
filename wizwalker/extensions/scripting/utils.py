import re
import time
from contextlib import suppress

from wizwalker.memory.memory_objects.enums import WindowFlags
from wizwalker.utils import maybe_wait_for_value_with_timeout


_friend_list_entry = re.compile(
    r"<Y;\d+><X;\d+><indent;0><Color;[\w\d]+><left>"
    r"<icon;FriendsList/Friend_Icon_List_0(?P<icon_list>[12])\."
    r"dds;\d+;\d+;(?P<icon_index>\d+)></left><Y;(?P<name_y>[-\d]+)><X;(?P<name_x>[-\d]+)>"
    r"<indent;\d+><Color;[\d\w]+>(<left>)?<COLOR;[\w\d]+>(?P<name>[\w ]+)"
)


def paint_window_for(window, seconds: float = 2):
    """
    Paint a window for a number of seconds

    Args:
        window: The window to paint
        seconds: How long to paint the window
    """
    start_time = time.perf_counter()
    while True:
        window.debug_paint()
        if time.perf_counter() - start_time >= seconds:
            break


def _maybe_get_named_window(parent, name: str):
    possible = parent.get_windows_with_name(name)

    if not possible:
        raise ValueError(f"No child window named {name}")

    if len(possible) > 1:
        raise ValueError(f"Multiple results for {name}")

    return possible[0]


def _cycle_to_online_friends(client, friends_list):
    list_label = _maybe_get_named_window(friends_list, "lblFriendsList")

    def _get_text():
        current_text = list_label.maybe_text()

        if current_text is None:
            raise Exception("Friend's list has no label")

        return current_text.replace("<center>", "").replace("</center>", "")

    right_button = _maybe_get_named_window(friends_list, "btnListTypeRight")

    while (current_page := _get_text()) != "Online Friends":
        client.mouse_handler.click_window(right_button)
        maybe_wait_for_value_with_timeout(
            _get_text, value=current_page, inverse_value=True, timeout=5
        )


def _cycle_friends_list(
    client, right_button, friends_list, icon, icon_list, name, current_page
):
    list_text = friends_list.maybe_text()

    match = None
    idx = 0

    for idx, friend_entry in enumerate(list(_friend_list_entry.finditer(list_text))):
        friend_icon = int(friend_entry.group("icon_index"))
        friend_icon_list = int(friend_entry.group("icon_list"))
        friend_name = friend_entry.group("name")

        if icon is not None and icon_list is not None and name:
            if (
                friend_icon == icon
                and friend_icon_list == icon_list
                and friend_name == name
            ):
                match = friend_entry
                break

        elif icon is not None and icon_list is not None:
            if friend_icon == icon and friend_icon_list == icon_list:
                match = friend_entry
                break

        elif name:
            if friend_name == name:
                match = friend_entry
                break

        else:
            raise RuntimeError("Invalid args")

    if match:
        target_page = (idx // 10) + 1

        if target_page != current_page:
            for _ in range(target_page - current_page):
                client.mouse_handler.click_window(right_button)

    return match, idx


def _click_on_friend(client, friends_list, friend_index):
    scaled_rect = friends_list.scale_to_client()
    ui_scale = client.render_context.ui_scale()

    # 12 % 10 = 2 * 30 = 60 * ui_scale
    scaled_friend_name_y = ((friend_index % 10) * 30) * ui_scale

    scaled_rect_center = scaled_rect.center()
    click_x = scaled_rect_center[0]
    # 15 is half the size of each entry's click area
    click_y = int(scaled_rect.y1 + scaled_friend_name_y + (15 * ui_scale))

    client.mouse_handler.click(click_x, click_y)
    time.sleep(1)


def _teleport_to_friend(client, character_window):
    teleport_button = _maybe_get_named_window(character_window, "btnGoToFriend")
    client.mouse_handler.click_window(teleport_button)
    # wait for confirmation window
    time.sleep(1)

    confirmation_window = _maybe_get_named_window(
        client.root_window, "MessageBoxModalWindow"
    )
    yes_button = _maybe_get_named_window(confirmation_window, "centerButton")

    close_button = _maybe_get_named_window(character_window, "btnCharacterClose")

    client.mouse_handler.click_window(yes_button)
    # we need to click the close button within the 1 second of the teleport animation

    # TODO: check for busy message error here -> race condition with needing to also click the close button
    #  could try forcing a zone wait since the busy condition will be handled here

    client.mouse_handler.click_window(close_button)


# TODO: add error if friend is busy message pops up
def teleport_to_friend_from_list(
    client, *, icon_list: int = None, icon_index: int = None, name: str = None
):
    """
    Teleport to a friend from the client's friend list

    Args:
        client: Client to teleport
        icon_list: Icon list the icon is from (1 or 2) or None
        icon_index: Index of the icon or None
        name: Name of the player or None
    """
    if (
        icon_list is None
        and icon_index is not None
        or icon_list is not None
        and icon_index is None
    ):
        raise ValueError("Icon list and icon index must both be defined or not defined")

    if all(i is None for i in (icon_list, icon_index, name)):
        raise ValueError("Must specify icon_list and icon_index or name or all")

    friends_window = _maybe_get_named_window(
        client.root_window, "NewFriendsListWindow"
    )

    # open friend's list if closed
    if not friends_window.is_visible():
        friend_button = _maybe_get_named_window(client.root_window, "btnFriends")

        client.mouse_handler.click_window(friend_button)

    _cycle_to_online_friends(client, friends_window)

    friends_list_window = _maybe_get_named_window(friends_window, "listFriends")
    friends_list_text = friends_list_window.maybe_text()

    # no friends online
    if not friends_list_text:
        raise ValueError("No friends online")

    right_button = _maybe_get_named_window(friends_window, "btnArrowDown")
    page_number = _maybe_get_named_window(friends_window, "PageNumber")

    page_number_text = page_number.maybe_text()

    current_page, _ = map(
        int,
        page_number_text.replace("<center>", "")
        .replace("</center>", "")
        .replace(" ", "")
        .split("/"),
    )

    friend, friend_index = _cycle_friends_list(
        client,
        right_button,
        friends_list_window,
        icon_index,
        icon_list,
        name,
        current_page,
    )

    if friend is None:
        raise ValueError(
            f"Could not find friend with icon {icon_index} icon list {icon_list} and/or name {name}"
        )

    _click_on_friend(client, friends_list_window, friend_index)

    character_window = _maybe_get_named_window(client.root_window, "wndCharacter")
    _teleport_to_friend(client, character_window)

    # close friends window
    friends_window.write_flags(WindowFlags(2147483648))


def get_window_from_path(root_window, name_path):
    """
    Returns a window by following a list of window names, the last window is returned
    Returns False if any window in the source_path can't be found
    """

    def _recurse_follow_path(window, path):
        if len(path) == 0:
            return window

        for child in window.children():
            if child.name() == path[0]:
                found_window = _recurse_follow_path(child, path[1:])
                if found_window:
                    return found_window

        return False

    return _recurse_follow_path(root_window, name_path)
