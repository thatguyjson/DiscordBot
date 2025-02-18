# DiscordBot by Json!

## Current Commands

```
?add_question <question> -- Allows for Owners to add questions to the live database
?ping -- The bot will return the ping in 'ms'
?kick <user> -- Allows for Owners to kick users
?evict <user> -- Allows for Owners to ban users
?role <user> <role> -- Allows for Owners to give a user a role by using a command
?praise <user> -- Alows for any member to send 1 of 11 random praise messages to a user
?purge <number> -- Allows for an Owner to delete the last {number} of messages sent in a channel
?timepurge <number> <units> -- Allows for an Owner to delete the last {number} of {units} of messages sent in a channel.
?readme -- Allows Owners to use requests to grab the data from the github readme.md and sends it via embeds on discord
?aboutme --
?createuser --
?upsertuserinfo --
```
## Current Bot Events
```
on_member_join -- When a new member joins, it automatically sends 1 of 11 random messages to the welcomeChannel
on_message_delete -- When a member deletes a message, it will be logged and sent to a Owners only channel
on_ready -- Runs when the bot starts up.
```
