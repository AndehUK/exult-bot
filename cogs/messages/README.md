# Message Manager

# Message Manager Main Menu ✅

- [Create Message](#message-builder-main-menu) ✅
- [Edit Message](#message-selector-edit) ✅
- [Delete Message(s)](#message-selector-delete) ✅
- [View Message](#message-selector-view) ✅
- Edit on Web ✅
  - URL button that redirects to web dashboard where they can view the web version of this menu
- Cancel ✅
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

## Message Builder Main Menu

- Message Content ✅
  - Modal, Max length 2000 ✅
- [Embeds](#embed-main-menu)
- Import JSON ✅
  - Modal, Max length 4000 ✅
- Save and Exit
  - Show modal prompting user to name the message, then update main embed saying "Complete"
  - Disable options if reached max for their tier
  - Disable save and exit button if guild and user are at max
- Save and Send
  - Show options, save to guild, save to user
    - Show modal prompting user to name the message
      - Prompt the user to select which channel they want to send the message to
        - Check send and read permissions for channel, if good then send and update main embed saying "Complete"
    - Disable options if reached max for their tier
  - Disable save and send button if guild and user are at max
- Send Without Saving ✅
  - Prompt the user to select which channel they want to send the message to
    - Check send and read permissions for channel, if good then send and update main embed saying "Complete"
- Cancel ✅
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

## Embed Main Menu

- [Create Embed](#embed-builder)
- [Edit Embed](#embed-selector-edit)
- [Delete Embed(s)](#embed-selector-delete)
- [Go Back](#message-create-main-menu)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

## Embed Builder

- Author ✅
  - Modal, 3 inputs for name, icon and url
- Title ✅
  - Modal, Max length 256
- Description ✅
  - Modal, Max length 2048
- Colour ✅
  - Modal, check value provided is valid colour value
- [Fields](#embed-fields)
- [Footer](#embed-footer)
- Thumbnail
  - Modal, check for valid image url
- Image
  - Modal, check for valid image url
- [Finish](#embed-main-menu)
- [Go Back](#embed-main-menu) ✅
- Cancel ✅
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

### Embed Fields

- [Add Field](#field-builder)
- [Edit Field](#field-selector-edit)
- [Delete Field(s)](#field-selector-delete)
- [Go Back](#embed-builder)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

#### Field Builder

- Field Name
  - Modal, Max length 256
- Field Value
  - Modal, Max length 1024
- Field Inline (Toggleable)
- [Confirm](#embed-fields)
- [Go Back](#embed-fields)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

#### Field Selector (Edit)

- [Field SelectMenu](#field-builder)
- [Go Back](#embed-fields)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

#### Field Selector (Delete)

- [Field SelectMenu](#embed-fields)
- [Go Back](#embed-fields)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

### Embed Footer

- Footer Text
  - Modal, Max length 2048
- Footer Icon
  - Modal, check for valid image url
- [Go Back](#embed-builder)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

## Embed Selector (Edit)

- [Embed SelectMenu](#embed-builder)
- [Go Back](#embed-main-menu)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

## Embed Selector (Delete)

- [Embed SelectMenu](#embed-builder)
- [Go Back](#embed-main-menu)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

## Message Selector (Edit)

- [Message SelectMenu](#message-builder-main-menu)
- [Go Back](#message-manager-main-menu)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

## Message Selector (Delete)

- [Message SelectMenu](#message-manager-main-menu)
- [Go Back](#message-manager-main-menu)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view

## Message Selector (View)

- [Message SelectMenu](#message-manager-main-menu)
  - Respond with an ephemeral message showing what the message selected contains
- [Go Back](#message-manager-main-menu)
- Cancel
  - Delete Message, give the user 5 minutes to restore from where they left off, then disable view
