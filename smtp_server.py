"""
SMTP Server Implementation
This server listens for incoming emails and delivers them to recipient mailboxes.
"""

import os
import json
import logging
from datetime import datetime
from email.parser import Parser
from email import policy
import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as SMTPProtocol

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smtp_server.log'),
        logging.StreamHandler()
    ]
)

class CustomSMTPHandler:
    """
    Custom SMTP Handler that processes incoming emails and delivers them to mailboxes.
    """
    
    def __init__(self, mailbox_dir='mailboxes'):
        self.mailbox_dir = mailbox_dir
        self.gui_log_queue = None  # For GUI logging
        
        # Create mailbox directory if it doesn't exist
        if not os.path.exists(self.mailbox_dir):
            os.makedirs(self.mailbox_dir)
            logging.info(f"Created mailbox directory: {self.mailbox_dir}")
            self._gui_log(f"Created mailbox directory: {self.mailbox_dir}\n")
    
    async def handle_DATA(self, server, session, envelope):
        """
        Process incoming email messages.
        
        Args:
            server: SMTP server instance
            session: Session information
            envelope: Email envelope containing mail_from, rcpt_tos, and content
        """
        try:
            peer = session.peer
            mailfrom = envelope.mail_from
            rcpttos = envelope.rcpt_tos
            data = envelope.content
            
            logging.info(f"Receiving email from: {peer}")
            logging.info(f"Sender: {mailfrom}")
            logging.info(f"Recipients: {rcpttos}")
            
            self._gui_log(f"📨 Receiving email from {mailfrom}\n")
            self._gui_log(f"   To: {', '.join(rcpttos)}\n")
            
            # Parse the email data
            msg = Parser(policy=policy.default).parsestr(data.decode('utf-8', errors='replace'))
            
            # Extract email details
            subject = msg.get('Subject', 'No Subject')
            from_addr = msg.get('From', mailfrom)
            to_addrs = msg.get('To', ', '.join(rcpttos))
            date = msg.get('Date', datetime.now().strftime('%a, %d %b %Y %H:%M:%S'))
            
            logging.info(f"Subject: {subject}")
            self._gui_log(f"   Subject: {subject}\n")
            
            # Deliver email to each recipient's mailbox
            for recipient in rcpttos:
                if self.validate_email(recipient):
                    self.deliver_to_mailbox(recipient, mailfrom, subject, data, msg)
                    logging.info(f"Email delivered to {recipient}")
                    self._gui_log(f"✓ Email delivered to {recipient}\n")
                else:
                    logging.warning(f"Invalid recipient email address: {recipient}")
                    self._gui_log(f"✗ Invalid recipient: {recipient}\n")
            
            logging.info("Email processing completed successfully\n")
            self._gui_log("\n")
            return '250 Message accepted for delivery'
            
        except Exception as e:
            logging.error(f"Error processing email: {str(e)}")
            return '550 Error processing message'
    
    def validate_email(self, email):
        """
        Basic email validation.
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if '@' in email and '.' in email.split('@')[1]:
            return True
        return False
    
    def deliver_to_mailbox(self, recipient, sender, subject, raw_data, parsed_msg):
        """
        Deliver email to recipient's mailbox.
        
        Args:
            recipient: Recipient email address
            sender: Sender email address
            subject: Email subject
            raw_data: Raw email data
            parsed_msg: Parsed email message object
        """
        try:
            # Create recipient mailbox if it doesn't exist
            recipient_safe = recipient.replace('@', '_at_').replace('.', '_')
            recipient_mailbox = os.path.join(self.mailbox_dir, recipient_safe)
            
            if not os.path.exists(recipient_mailbox):
                os.makedirs(recipient_mailbox)
            
            # Generate unique filename for email
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            email_filename = f"email_{timestamp}.eml"
            email_path = os.path.join(recipient_mailbox, email_filename)
            
            # Save raw email data
            with open(email_path, 'wb') as f:
                f.write(raw_data if isinstance(raw_data, bytes) else raw_data.encode('utf-8'))
            
            # Save email metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'from': sender,
                'to': recipient,
                'subject': subject,
                'filename': email_filename
            }
            
            metadata_path = os.path.join(recipient_mailbox, f"metadata_{timestamp}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)
            
            logging.info(f"Email saved to: {email_path}")
            
        except Exception as e:
            logging.error(f"Error delivering to mailbox: {str(e)}")
            raise
    
    def _gui_log(self, message):
        """Send log message to GUI if available"""
        if self.gui_log_queue:
            try:
                self.gui_log_queue.put(message)
            except:
                pass


def start_server(host='127.0.0.1', port=1025):
    """
    Start the SMTP server.
    
    Args:
        host: Server host address (default: localhost)
        port: Server port (default: 1025, non-privileged port)
    """
    try:
        handler = CustomSMTPHandler()
        controller = Controller(handler, hostname=host, port=port)
        
        print(f"\n{'='*60}")
        print(f"SMTP Server is running on {host}:{port}")
        print(f"Mailboxes will be stored in './mailboxes' directory")
        print(f"Logs are being written to 'smtp_server.log'")
        print(f"Press Ctrl+C to stop the server")
        print(f"{'='*60}\n")
        
        controller.start()
        logging.info(f"SMTP Server started on {host}:{port}")
        
        # Keep the server running
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        print("\nServer stopped.")
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        print(f"Error: {str(e)}")
    finally:
        if 'controller' in locals():
            controller.stop()


if __name__ == '__main__':
    # You can change these values or add command-line argument parsing
    HOST = '127.0.0.1'  # localhost
    PORT = 1025         # Use non-privileged port (>1024)
    
    start_server(HOST, PORT)
