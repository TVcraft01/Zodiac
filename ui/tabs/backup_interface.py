"""
Interface de secours en cas d'échec de la nouvelle interface
"""
import tkinter as tk
from tkinter import scrolledtext

def launch_backup():
    """Lance une interface simple de secours"""
    root = tk.Tk()
    root.title("Zodiac OS - Mode de secours")
    root.geometry("800x500")
    
    # Titre
    title = tk.Label(
        root,
        text="⚠️ ZODIAC OS - MODE DE SECOURS",
        font=("Arial", 20, "bold"),
        fg="orange"
    )
    title.pack(pady=20)
    
    # Message
    message = tk.Label(
        root,
        text="L'interface principale a rencontré une erreur.\n\n" +
             "Veuillez vérifier:\n" +
             "1. Que CustomTkinter est installé (pip install customtkinter)\n" +
             "2. Que Pillow est installé (pip install pillow)\n" +
             "3. Que la structure des dossiers est correcte\n\n" +
             "Consultez la console pour plus de détails.",
        font=("Arial", 12),
        justify="left"
    )
    message.pack(pady=20, padx=50)
    
    # Console de log
    log_label = tk.Label(root, text="Logs:", font=("Arial", 10, "bold"))
    log_label.pack(anchor="w", padx=50)
    
    log_text = scrolledtext.ScrolledText(root, height=10, width=70)
    log_text.pack(padx=50, pady=(0, 20))
    log_text.insert(tk.END, "Les logs d'erreur s'afficheront ici...")
    
    # Bouton de fermeture
    tk.Button(
        root,
        text="Fermer",
        command=root.quit,
        font=("Arial", 12),
        bg="red",
        fg="white",
        padx=20,
        pady=10
    ).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    launch_backup()