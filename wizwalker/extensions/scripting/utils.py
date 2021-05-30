import asyncio
import re
from contextlib import suppress

from wizwalker.memory.memory_objects.enums import WindowFlags


_friend_list_entry = re.compile(
    r"<Y;\d+><X;\d+><indent;0><Color;[\w\d]+><left>"
    r"<icon;FriendsList/Friend_Icon_List_0(?P<icon_list>[12])\."
    r"dds;\d+;\d+;(?P<icon_index>\d)+></left><Y;(?P<name_y>[-\d]+)><X;(?P<name_x>[-\d]+)>"
    r"<indent;\d+><Color;[\d\w]+><left><COLOR;[\w\d]+>(?P<name>[\w ]+)"
)

_friend_list_type_cycle = {
    "Online Friends": 0,
    "Friend Chat": 3,
    "All Friends": 2,
    "Ignored": 1,
}


async def paint_window_for(window, time: float = 2):
    """
    Paint a window for a number of seconds

    Args:
        window: The window to paint
        time: How long to paint the window
    """

    async def _paint_task():
        with suppress(asyncio.CancelledError):
            while True:
                await window.debug_paint()

    paint_task = asyncio.create_task(_paint_task())
    await asyncio.sleep(time)
    paint_task.cancel()


async def _maybe_get_named_window(parent, name: str):
    possible = await parent.get_windows_with_name(name)

    if not possible:
        raise ValueError(f"No child window named {name}")

    if len(possible) > 1:
        raise ValueError(f"Multiple results for {name}")

    return possible[0]


async def _cycle_to_online_friends(client, friends_list):
    list_label = await _maybe_get_named_window(friends_list, "lblFriendsList")

    current_text = await list_label.maybe_text()

    if current_text is None:
        raise Exception("Friend's list has no label")

    current_page = current_text.replace("<center>", "").replace("</center>", "")

    right_button = await _maybe_get_named_window(friends_list, "btnListTypeRight")

    for _ in range(_friend_list_type_cycle[current_page]):
        await client.mouse_handler.click_window(right_button)
        await asyncio.sleep(1)


async def _cycle_friends_list(
    client, right_button, friends_list, page_number, icon, icon_list, name
):
    page_number_text = await page_number.maybe_text()

    current, total = map(
        int,
        page_number_text.replace("<center>", "")
        .replace("</center>", "")
        .replace(" ", "")
        .split("/"),
    )

    for page in range(total):
        list_text = await friends_list.maybe_text()

        for friend_entry in _friend_list_entry.finditer(list_text):
            friend_icon = int(friend_entry.group("icon_index"))
            friend_icon_list = int(friend_entry.group("icon_list"))
            friend_name = friend_entry.group("name")

            if icon is not None and icon_list is not None and name:
                if (
                    friend_icon == icon
                    and friend_icon_list == icon_list
                    and friend_name == name
                ):
                    return friend_entry

            elif icon is not None and icon_list is not None:
                if friend_icon == icon and friend_icon_list == icon_list:
                    return friend_entry

            elif name:
                if friend_name == name:
                    return friend_entry

            else:
                raise RuntimeError("Invalid args")

        if page < total:
            await client.mouse_handler.click_window(right_button)

        else:
            return None


async def _click_on_friend(client, friends_list, friend_name_x, friend_name_y):
    scaled_rect = await friends_list.scale_to_client()
    ui_scale = await client.render_context.ui_scale()

    scaled_friend_name_x = friend_name_x * ui_scale
    scaled_friend_name_y = friend_name_y * ui_scale

    scaled_rect_center = scaled_rect.center()
    click_x = scaled_rect_center[0]
    click_y = int(scaled_rect.y1 + scaled_friend_name_y + (scaled_friend_name_x / 2))

    await client.mouse_handler.click(click_x, click_y)
    await asyncio.sleep(1)


async def _teleport_to_friend(client, character_window):
    teleport_button = await _maybe_get_named_window(character_window, "btnGoToFriend")
    await client.mouse_handler.click_window(teleport_button)
    # wait for confirmation window
    await asyncio.sleep(1)

    confirmation_window = await _maybe_get_named_window(
        client.root_window, "MessageBoxModalWindow"
    )
    yes_button = await _maybe_get_named_window(confirmation_window, "centerButton")

    close_button = await _maybe_get_named_window(character_window, "btnCharacterClose")

    await client.mouse_handler.click_window(yes_button)
    # we need to click the close button within the 1 second of the teleport animation
    await client.mouse_handler.click_window(close_button)


# TODO: test if multipage works
async def teleport_to_friend_from_list(
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

    friends_window = await _maybe_get_named_window(
        client.root_window, "NewFriendsListWindow"
    )

    # open friend's list if closed
    if not await friends_window.is_visible():
        friend_button = await _maybe_get_named_window(client.root_window, "btnFriends")

        await client.mouse_handler.click_window(friend_button)

    await _cycle_to_online_friends(client, friends_window)

    friends_list_window = await _maybe_get_named_window(friends_window, "listFriends")
    friends_list_text = await friends_list_window.maybe_text()

    # no friends online
    if not friends_list_text:
        # TODO: change error
        raise Exception("No friends online")

    right_button = await _maybe_get_named_window(friends_window, "btnArrowDown")
    page_number = await _maybe_get_named_window(friends_window, "PageNumber")

    friend = await _cycle_friends_list(
        client,
        right_button,
        friends_list_window,
        page_number,
        icon_index,
        icon_list,
        name,
    )

    if friend is None:
        raise ValueError(
            f"Could not find friend with icon {icon_index} icon list {icon_list} and/or name {name}"
        )

    name_x, name_y = map(int, (friend.group("name_x"), friend.group("name_y")))
    await _click_on_friend(client, friends_list_window, name_x, name_y)

    character_window = await _maybe_get_named_window(client.root_window, "wndCharacter")
    await _teleport_to_friend(client, character_window)

    # close friends window
    await friends_window.write_flags(WindowFlags(2147483648))


# --- [NewFriendsListWindow] NewFriendsListWindow
# ---- [wndFriendsListScroll] Window

# list container
# ----- [listFriends] ControlList

# close list
# ---- [btnClose] ControlButton

# cycle through different pages of list
# ---- [btnArrowUp] ControlButton
# ---- [btnArrowDown] ControlButton

# ---- [MoreFriendsButton] ControlButton
# ---- [PageNumber] ControlText

# cycle though all friends -> online friends
# ---- [btnListTypeLeft] ControlButton
# ---- [btnListTypeRight] ControlButton

# ---- [btnLeaveParty] ControlButton
# ---- [Layout] Window

# name of list
# ----- [lblFriendsList] ControlText

# ---- [btnLeaveChatChannel] ControlButton
# ---- [btnInviteAllChatChannel] ControlButton


# --- [wndCharacter] CharacterWindow

# close character window
# ---- [btnCharacterClose] ControlButton

# ---- [ButtonLayout] WindowLayout
# ----- [btnRemoveFriend] ControlButton
# ----- [btnIgnore] ControlButton
# ----- [btnReport] ControlButton
# ----- [btnSendAway] ControlButton
# ----- [btnRemoveChatChannel] ControlButton
# ---- [FriendStatusRecent] ControlSprite
# ---- [FriendStatusActive] ControlSprite
# ---- [FriendStatusDormant] ControlSprite
# ---- [ButtonLayout] WindowLayout
# ----- [btnCharacterInspection] ControlButton
# ----- [btnAddRemoveFriend] ControlButton

# teleport to friend
# ----- [btnGoToFriend] ControlButton

# ----- [btnTrade] ControlButton
# ----- [btnHatch] ControlButton
# ----- [btnInvite] ControlButton
# ----- [btnFriendFinder] ControlButton
# ----- [btnSecureChat] ControlButton
# ----- [btnQuickChat] ScrollablePopupButton
# ----- [btnJoinChatChannel] ControlButton
# ---- [lblCharacterName] ControlText
# ---- [ClipWindow] Window
# ----- [wndCharacterPortrait] PreviewWindow
# ---- [FriendsSinceLabel] ControlText
# ---- [FriendsSinceText] ControlText


# - [MessageBoxModalWindow] MessageBoxWindow
# -- [messageBoxBG] Window
# --- [Top] ControlSprite
# --- [Bottom] ControlSprite
# --- [Left] ControlSprite
# --- [Right] ControlSprite
# --- [TopLeft] ControlSprite
# --- [TopRight] ControlSprite
# --- [BottomLeft] ControlSprite
# --- [TopLeft] ControlSprite
# --- [messageBoxLayout] WindowLayout
# ---- [] Window
# ----- [TitleText] ControlText
# ---- [TextArea] Window
# ----- [CaptionText] ControlText
# ---- [ignoreCheckBox] ControlCheckBox
# ---- [AdjustmentWindow] Window
# ----- [Layout] WindowLayout
# ------ [centerButton] ControlButton
# ------ [leftButton] ControlButton
# ------ [rightButton] ControlButton
