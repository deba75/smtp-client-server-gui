"""
SMTP Lab GUI Application
Cross-platform GUI for SMTP client and server using tkinter.
Compatible with Windows, Mac, and Linux.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import json
import os
from datetime import datetime
from smtp_client import SMTPClient
from smtp_server import CustomSMTPHandler, logging
from aiosmtpd.controller import Controller
import time


class SMTPLabGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SMTP Lab - Email Client & Server")
        self.root.geometry("1000x700")
        
        # Server state
        self.server_controller = None
        self.server_running = False
        self.server_thread = None
        
        # Queue for server logs
        self.log_queue = queue.Queue()
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam' if 'clam' in style.theme_names() else 'default')
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_server_tab()
        self.create_client_tab()
        self.create_mailbox_tab()
        
        # Start log update loop
        self.update_logs()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_server_tab(self):
        """Create server control tab"""
        server_frame = ttk.Frame(self.notebook)
        self.notebook.add(server_frame, text="📬 Server")
        
        # Server controls
        control_frame = ttk.LabelFrame(server_frame, text="Server Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Host and Port
        config_frame = ttk.Frame(control_frame)
        config_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(config_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.server_host = tk.StringVar(value="127.0.0.1")
        ttk.Entry(config_frame, textvariable=self.server_host, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.server_port = tk.StringVar(value="1025")
        ttk.Entry(config_frame, textvariable=self.server_port, width=10).grid(row=0, column=3, padx=5)
        
        # Start/Stop buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(button_frame, text="▶ Start Server", 
                                     command=self.start_server, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ Stop Server", 
                                    command=self.stop_server, width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.server_status = tk.StringVar(value="⚫ Server Stopped")
        status_label = ttk.Label(button_frame, textvariable=self.server_status, 
                                font=('Arial', 10, 'bold'))
        status_label.pack(side=tk.LEFT, padx=20)
        
        # Server logs
        log_frame = ttk.LabelFrame(server_frame, text="Server Logs", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.server_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                     height=20, font=('Courier', 9))
        self.server_log.pack(fill=tk.BOTH, expand=True)
        
        # Add initial helpful message
        self.server_log.insert(tk.END, "═" * 60 + "\n")
        self.server_log.insert(tk.END, "SMTP Server Control Panel\n")
        self.server_log.insert(tk.END, "═" * 60 + "\n\n")
        self.server_log.insert(tk.END, "👉 Click 'Start Server' button above to begin receiving emails\n\n")
        self.server_log.insert(tk.END, "Server will listen on the specified host and port.\n")
        self.server_log.insert(tk.END, "Default: 127.0.0.1:1025 (localhost)\n\n")
        self.server_log.insert(tk.END, "Logs will appear here when the server is running...\n")
        self.server_log.insert(tk.END, "═" * 60 + "\n\n")
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Logs", 
                   command=lambda: self.server_log.delete(1.0, tk.END)).pack(pady=5)
    
    def create_client_tab(self):
        """Create email client tab"""
        client_frame = ttk.Frame(self.notebook)
        self.notebook.add(client_frame, text="📧 Send Email")
        
        # Email composition
        compose_frame = ttk.LabelFrame(client_frame, text="Compose Email", padding=10)
        compose_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Server settings
        server_frame = ttk.Frame(compose_frame)
        server_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(server_frame, text="SMTP Server:").pack(side=tk.LEFT, padx=5)
        self.client_host = tk.StringVar(value="127.0.0.1")
        ttk.Entry(server_frame, textvariable=self.client_host, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(server_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.client_port = tk.StringVar(value="1025")
        ttk.Entry(server_frame, textvariable=self.client_port, width=8).pack(side=tk.LEFT, padx=5)
        
        # From
        ttk.Label(compose_frame, text="From:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_from = tk.StringVar(value="sender@example.com")
        ttk.Entry(compose_frame, textvariable=self.email_from, width=50).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # To
        ttk.Label(compose_frame, text="To:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_to = tk.StringVar(value="recipient@example.com")
        to_entry = ttk.Entry(compose_frame, textvariable=self.email_to, width=50)
        to_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(compose_frame, text="(comma-separated for multiple)", 
                 font=('Arial', 8), foreground='gray').grid(row=2, column=2, sticky=tk.W, padx=5)
        
        # Subject
        ttk.Label(compose_frame, text="Subject:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.email_subject = tk.StringVar(value="Test Email")
        ttk.Entry(compose_frame, textvariable=self.email_subject, width=50).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Body
        ttk.Label(compose_frame, text="Message:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.email_body = scrolledtext.ScrolledText(compose_frame, wrap=tk.WORD, 
                                                     height=10, width=60, font=('Arial', 10))
        self.email_body.grid(row=4, column=1, pady=5, sticky=tk.W)
        self.email_body.insert(1.0, "Hello,\n\nThis is a test email from SMTP Lab.\n\nBest regards")
        
        # Attachments
        attach_frame = ttk.Frame(compose_frame)
        attach_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(compose_frame, text="Attachments:").grid(row=5, column=0, sticky=tk.NW, pady=5)
        self.attachments = []
        self.attachment_listbox = tk.Listbox(attach_frame, height=3, width=50)
        self.attachment_listbox.pack(side=tk.LEFT)
        
        attach_btn_frame = ttk.Frame(attach_frame)
        attach_btn_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(attach_btn_frame, text="➕ Add", width=8, 
                   command=self.add_attachment).pack(pady=2)
        ttk.Button(attach_btn_frame, text="➖ Remove", width=8, 
                   command=self.remove_attachment).pack(pady=2)
        
        # Send button
        send_frame = ttk.Frame(compose_frame)
        send_frame.grid(row=6, column=1, pady=10)
        
        ttk.Button(send_frame, text="📤 Send Email", command=self.send_email, 
                   width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(send_frame, text="🔄 Clear Form", command=self.clear_form, 
                   width=20).pack(side=tk.LEFT, padx=5)
        
        # Server status warning
        self.client_warning = tk.Label(compose_frame, 
                                       text="⚠️ Remember to start the server first (Server tab)",
                                       font=('Arial', 9, 'bold'),
                                       foreground='orange',
                                       background='lightyellow',
                                       padx=10, pady=5)
        self.client_warning.grid(row=0, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        # Send status
        self.send_status = scrolledtext.ScrolledText(compose_frame, wrap=tk.WORD, 
                                                      height=6, width=60, font=('Courier', 9))
        self.send_status.grid(row=7, column=1, pady=5)
    
    def create_mailbox_tab(self):
        """Create mailbox viewer tab"""
        mailbox_frame = ttk.Frame(self.notebook)
        self.notebook.add(mailbox_frame, text="📬 Mailbox")
        
        # Controls
        control_frame = ttk.Frame(mailbox_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="🔄 Refresh", 
                   command=self.refresh_mailbox).pack(side=tk.LEFT, padx=5)
        ttk.Label(control_frame, text="Select Mailbox:").pack(side=tk.LEFT, padx=10)
        
        self.mailbox_var = tk.StringVar()
        self.mailbox_combo = ttk.Combobox(control_frame, textvariable=self.mailbox_var, 
                                          width=30, state='readonly')
        self.mailbox_combo.pack(side=tk.LEFT, padx=5)
        self.mailbox_combo.bind('<<ComboboxSelected>>', self.load_emails)
        
        # Split view
        paned = ttk.PanedWindow(mailbox_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Email list
        list_frame = ttk.LabelFrame(paned, text="Emails", padding=5)
        
        # Treeview for email list
        columns = ('From', 'Subject', 'Date')
        self.email_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=10)
        
        self.email_tree.heading('#0', text='#')
        self.email_tree.column('#0', width=40)
        self.email_tree.heading('From', text='From')
        self.email_tree.column('From', width=200)
        self.email_tree.heading('Subject', text='Subject')
        self.email_tree.column('Subject', width=300)
        self.email_tree.heading('Date', text='Date')
        self.email_tree.column('Date', width=150)
        
        self.email_tree.pack(fill=tk.BOTH, expand=True)
        self.email_tree.bind('<<TreeviewSelect>>', self.view_email)
        
        paned.add(list_frame)
        
        # Email content viewer
        content_frame = ttk.LabelFrame(paned, text="Email Content", padding=5)
        
        self.email_content = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                                        height=15, font=('Arial', 10))
        self.email_content.pack(fill=tk.BOTH, expand=True)
        
        paned.add(content_frame)
        
        # Initial load
        self.refresh_mailbox()
    
    def start_server(self):
        """Start SMTP server"""
        try:
            host = self.server_host.get()
            port = int(self.server_port.get())
            
            def run_server():
                handler = CustomSMTPHandler()
                # Redirect handler logs to GUI
                handler.gui_log_queue = self.log_queue
                
                self.server_controller = Controller(handler, hostname=host, port=port)
                self.server_controller.start()
                
                self.log_queue.put(f"✓ SMTP Server started on {host}:{port}\n")
                
                # Keep server running
                while self.server_running:
                    time.sleep(0.1)
            
            self.server_running = True
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Update UI
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.server_status.set("🟢 Server Running")
            self.log_message(self.server_log, f"✓ Server started on {host}:{port}\n", 'green')
            
            # Hide warning in client tab if using same host
            if hasattr(self, 'client_warning'):
                self.client_warning.grid_remove()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
    
    def stop_server(self):
        """Stop SMTP server"""
        try:
            self.server_running = False
            
            if self.server_controller:
                self.server_controller.stop()
                self.server_controller = None
            
            # Update UI
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.server_status.set("⚫ Server Stopped")
            self.log_message(self.server_log, "⏹ Server stopped.\n", 'red')
            
            # Show warning in client tab
            if hasattr(self, 'client_warning'):
                self.client_warning.grid()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")
    
    def send_email(self):
        """Send email using SMTP client"""
        try:
            # Get values
            host = self.client_host.get()
            port = int(self.client_port.get())
            sender = self.email_from.get()
            recipients = [r.strip() for r in self.email_to.get().split(',')]
            subject = self.email_subject.get()
            body = self.email_body.get(1.0, tk.END).strip()
            
            # Validate
            if not sender or not recipients or not subject:
                messagebox.showwarning("Missing Information", "Please fill in all required fields")
                return
            
            # Check if server is running (if using localhost)
            if not self.server_running and host in ['127.0.0.1', 'localhost']:
                response = messagebox.askyesno(
                    "Server Not Running",
                    "⚠️ The SMTP server is not running!\n\n"
                    "You need to start the server first from the 'Server' tab.\n\n"
                    "Would you like to go to the Server tab now?",
                    icon='warning'
                )
                if response:
                    self.notebook.select(0)  # Switch to Server tab
                return
            
            # Send in thread to not block GUI
            def send_thread():
                try:
                    self.log_message(self.send_status, 
                                   f"📤 Sending email...\n", 
                                   'blue')
                    
                    client = SMTPClient(host, port)
                    success = client.send_email(sender, recipients, subject, body, 
                                               self.attachments if self.attachments else None)
                    
                    if success:
                        self.log_message(self.send_status, 
                                       f"✓ Email sent successfully!\n  From: {sender}\n  To: {', '.join(recipients)}\n  Subject: {subject}\n\n", 
                                       'green')
                        # Auto-refresh mailbox
                        self.root.after(1000, self.refresh_mailbox)
                    else:
                        self.log_message(self.send_status, 
                                       f"✗ Failed to send email.\n"
                                       f"  Make sure the SMTP server is running (Server tab).\n"
                                       f"  Server: {host}:{port}\n\n", 
                                       'red')
                except Exception as e:
                    self.log_message(self.send_status, 
                                   f"✗ Connection Error: {str(e)}\n"
                                   f"  Make sure the server is running on {host}:{port}\n\n", 
                                   'red')
            
            threading.Thread(target=send_thread, daemon=True).start()
            
        except Exception as e:
            self.log_message(self.send_status, f"✗ Error: {str(e)}\n\n", 'red')
    
    def add_attachment(self):
        """Add file attachment"""
        files = filedialog.askopenfilenames(title="Select files to attach")
        for file in files:
            if file not in self.attachments:
                self.attachments.append(file)
                self.attachment_listbox.insert(tk.END, os.path.basename(file))
    
    def remove_attachment(self):
        """Remove selected attachment"""
        selection = self.attachment_listbox.curselection()
        if selection:
            index = selection[0]
            self.attachment_listbox.delete(index)
            self.attachments.pop(index)
    
    def clear_form(self):
        """Clear email form"""
        self.email_from.set("sender@example.com")
        self.email_to.set("recipient@example.com")
        self.email_subject.set("Test Email")
        self.email_body.delete(1.0, tk.END)
        self.email_body.insert(1.0, "Hello,\n\nThis is a test email from SMTP Lab.\n\nBest regards")
        self.attachments.clear()
        self.attachment_listbox.delete(0, tk.END)
        self.send_status.delete(1.0, tk.END)
    
    def refresh_mailbox(self):
        """Refresh mailbox list"""
        mailbox_dir = 'mailboxes'
        if os.path.exists(mailbox_dir):
            mailboxes = [d.replace('_at_', '@').replace('_', '.') 
                        for d in os.listdir(mailbox_dir) 
                        if os.path.isdir(os.path.join(mailbox_dir, d))]
            self.mailbox_combo['values'] = mailboxes
            if mailboxes:
                self.mailbox_combo.current(0)
                self.load_emails()
        else:
            self.mailbox_combo['values'] = []
    
    def load_emails(self, event=None):
        """Load emails for selected mailbox"""
        # Clear tree
        for item in self.email_tree.get_children():
            self.email_tree.delete(item)
        
        mailbox = self.mailbox_var.get()
        if not mailbox:
            return
        
        mailbox_safe = mailbox.replace('@', '_at_').replace('.', '_')
        mailbox_path = os.path.join('mailboxes', mailbox_safe)
        
        if not os.path.exists(mailbox_path):
            return
        
        # Load metadata files
        emails = []
        for file in os.listdir(mailbox_path):
            if file.endswith('.json'):
                with open(os.path.join(mailbox_path, file), 'r') as f:
                    metadata = json.load(f)
                    emails.append(metadata)
        
        # Sort by timestamp (newest first)
        emails.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Add to tree
        for i, email in enumerate(emails, 1):
            self.email_tree.insert('', tk.END, text=str(i), 
                                  values=(email.get('from', 'Unknown'),
                                         email.get('subject', 'No Subject'),
                                         email.get('timestamp', '')[:19]),
                                  tags=(email.get('filename', ''),))
    
    def view_email(self, event=None):
        """View selected email content"""
        selection = self.email_tree.selection()
        if not selection:
            return
        
        item = self.email_tree.item(selection[0])
        eml_filename = item['tags'][0] if item['tags'] else None
        
        if not eml_filename:
            return
        
        mailbox = self.mailbox_var.get()
        mailbox_safe = mailbox.replace('@', '_at_').replace('.', '_')
        eml_path = os.path.join('mailboxes', mailbox_safe, eml_filename)
        
        if os.path.exists(eml_path):
            try:
                from email.parser import Parser
                from email import policy
                
                with open(eml_path, 'rb') as f:
                    msg = Parser(policy=policy.default).parse(f)
                
                # Clear content
                self.email_content.delete(1.0, tk.END)
                
                # Display headers
                self.email_content.insert(tk.END, f"From: {msg.get('From', 'Unknown')}\n", 'bold')
                self.email_content.insert(tk.END, f"To: {msg.get('To', 'Unknown')}\n", 'bold')
                self.email_content.insert(tk.END, f"Subject: {msg.get('Subject', 'No Subject')}\n", 'bold')
                self.email_content.insert(tk.END, f"Date: {msg.get('Date', 'Unknown')}\n", 'bold')
                self.email_content.insert(tk.END, "\n" + "-"*60 + "\n\n")
                
                # Display body
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                            self.email_content.insert(tk.END, body)
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='replace')
                    self.email_content.insert(tk.END, body)
                
                # Show attachments
                if msg.is_multipart():
                    attachments = [part.get_filename() for part in msg.walk() 
                                  if part.get_filename()]
                    if attachments:
                        self.email_content.insert(tk.END, f"\n\n" + "-"*60 + "\n")
                        self.email_content.insert(tk.END, f"Attachments ({len(attachments)}):\n", 'bold')
                        for att in attachments:
                            self.email_content.insert(tk.END, f"  📎 {att}\n")
                
                # Configure tags
                self.email_content.tag_config('bold', font=('Arial', 10, 'bold'))
                
            except Exception as e:
                self.email_content.delete(1.0, tk.END)
                self.email_content.insert(tk.END, f"Error reading email: {str(e)}")
    
    def log_message(self, widget, message, color=None):
        """Log message to text widget"""
        widget.insert(tk.END, message)
        if color:
            # Color the last line
            color_map = {
                'blue': '#0066cc',
                'green': '#008000',
                'red': '#cc0000'
            }
            widget.tag_config(color, foreground=color_map.get(color, color))
            start = widget.index(f"end-{len(message)}c")
            widget.tag_add(color, start, tk.END)
        widget.see(tk.END)
    
    def update_logs(self):
        """Update server logs from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_message(self.server_log, message)
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(100, self.update_logs)
    
    def on_closing(self):
        """Handle window closing"""
        if self.server_running:
            if messagebox.askokcancel("Quit", "Server is running. Stop server and quit?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = SMTPLabGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
