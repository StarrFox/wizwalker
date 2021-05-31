.. module:: wizwalker

.. toctree::
   :maxdepth: 5

ClientHandler
=============

.. autoclass:: ClientHandler
   :members:

Client
======

.. autoclass:: Client
   :members:

Combat
======

CombatHandler
~~~~~~~~~~~~~

.. autoclass:: wizwalker.combat.CombatHandler
    :members:

CombatMember
~~~~~~~~~~~~

.. autoclass:: wizwalker.combat.CombatMember
    :members:

CombatCard
~~~~~~~~~~

.. autoclass:: wizwalker.combat.CombatCard
    :members:

XYZ
===

.. autoclass:: XYZ
    :members:

Rectangle
=========

.. autoclass:: Rectangle
    :members:

MouseHandler
============

.. autoclass:: MouseHandler
    :members:

Constants
=========

.. autoclass:: Keycode
   :members:

Hotkey
======

ModifierKeys
~~~~~~~~~~~~

.. autoclass:: ModifierKeys
    :members:

Hotkey
~~~~~~

.. autoclass:: Hotkey
    :members:

Listener
~~~~~~~~

.. autoclass:: Listener
   :members:

HotkeyListener
~~~~~~~~~~~~~~

..autoclass:: HotkeyListener
    :members:

Memory
======

HookHandler
~~~~~~~~~~~

.. autoclass:: wizwalker.memory.HookHandler
    :members:

MemoryReader
~~~~~~~~~~~~

.. autoclass:: wizwalker.memory.MemoryReader
    :members:

Errors
======

.. autoexception:: WizWalkerError

.. autoexception:: ClientClosedError

.. autoexception:: HookNotActive

.. autoexception:: HookAlreadyActivated

.. autoexception:: WizWalkerMemoryError

.. autoexception:: PatternMultipleResults

.. autoexception:: PatternFailed

.. autoexception:: MemoryReadError

.. autoexception:: MemoryWriteError

.. autoexception:: ReadingEnumFailed

.. autoexception:: HookNotReady

.. autoexception:: WizWalkerCombatError

.. autoexception:: NotInCombat

.. autoexception:: NotEnoughPips

.. autoexception:: NotEnoughMana

.. autoexception:: CardAlreadyEnchanted

.. autoexception:: HotkeyAlreadyRegistered
