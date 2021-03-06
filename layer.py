from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities import OutgoingAckProtocolEntity
import logging

class MessageLayer(YowInterfaceLayer):
    """ This class receives messages. """
    
    def reply(self, message, text):
        message_out = TextMessageProtocolEntity(
            text,
            to = message.getFrom()
        )
        self.toLower(message_out)
    
    @ProtocolEntityCallback("message")
    def onMessage(self, message):
        """ Receive messages """
        
        message.setBody(message.getBody().strip()[1:]) # Strip EOT and \n, skip SOH character
        
        logging.debug("Received: {} - {}".format(message.getFrom(), message.getBody()))
        
        if not hasattr(self, "bot"):
            # Get the bot from the stack
            self.bot = self.getStack().bot
            self.bot.set_layer(self)
        
        # Notify the whatsapp servers we read the message so we don't receive it again
        receipt = OutgoingReceiptProtocolEntity(message.getId(), message.getFrom(), 'read', message.getParticipant())
        
        # Parse command
        self.bot.parse_commands(message)
        
        # Send receipt
        self.toLower(receipt)
        
        """
        # Commented out, will now be handled by the Bot
        # Create a message: TextMessageProtocolEntity("text to send", to=user_to_send_to), we will always want to use `to=message.getFrom()`
        message_out = TextMessageProtocolEntity(
            message.getBody(),
            to = message.getFrom()
        )

        # self.toLower(message_out) # Using self.toLower(message_to_send) should send a message.
        """

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        """ Acknowledge the receipt """
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)