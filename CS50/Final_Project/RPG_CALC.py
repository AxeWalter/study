import tkinter as tk

class GUI():
    def __init__(self):

        self.root = tk.Tk()

        self.root.configure(background = "#333333")

        self.root.geometry("300x250")
        self.root.title("Lazy XP Calculator")

        self.label = tk.Label(self.root, text="Graphic Design is My Passion s2\n\nInsert your total XP",
                              font=("Comic Sans MS", 12), bg = "#333333", fg = "yellow")
        self.label.pack(padx=10)

        self.xp_entry = tk.Entry(self.root, justify = "center")
        self.xp_entry.pack(pady = 5)

        self.xp_entry.bind("<Return>", self.calculate_on_enter)

        self.button = tk.Button(self.root, text= "Calculate", font=("Comic Sans MS", 8),
                                bg = "#333333", fg = "yellow", command = self.calculate)
        self.button.pack(pady = 8)

        self.result_label = tk.Label(self.root, text = "", font = ("Comic Sans MS", 12), bg = "#333333", fg = "yellow")
        self.result_label.pack(pady = 5)

        self.weak_button = tk.Button(self.root, text = "Am I weak?", font=("Garamond", 10), bg = "purple", fg = "gold",
                                    command = self.is_weak)
        self.weak_button.place(relx=0.98, rely=0.98, anchor='se')

        self.root.mainloop()

    def calculate(self):
        try:
            x = int(self.xp_entry.get())
            lvl = 0
            while x >= (lvl + 1) * 100:
                x = x - ((lvl + 1) * 100)
                lvl += 1

            self.result_label.config(text=f"Your current level is {lvl}\nAnd your remaining XP is {x}")

        except ValueError:
            pop = tk.Tk()
            pop.geometry("300x300")
            pop.configure(background = "black")
            pop.title("Stop PLEASE!")

            line1 = tk.Label(pop, text="Can You PLEASE", font=("Comic Sans MS", 16), bg = "black", fg = "green")
            line1.pack(pady =10)

            line2 = tk.Label(pop, text="Stop Trying to Break This", font = ("Helvetica", 16), bg = "black", fg = "pink")
            line2.pack(pady = 10)

            line3 = tk.Label(pop, text="And Insert", font=("Arial", 16), bg="black", fg="yellow")
            line3.pack(pady=10)

            line4 = tk.Label(pop, text="A Number???", font=("Bell Gothic Std Black", 16), bg="black", fg="purple")
            line4.pack(pady=10)

            line5 = tk.Label(pop, text="Thank YOU!!!", font=("Minion Pro Med", 16), bg="black", fg="red")
            line5.pack(pady=10)

            line6 = tk.Label(pop, text="Also, Sonei will never hit a shot :)",
                             font=("Kozuka Mincho Pro M", 8), bg="black", fg="cyan")
            line6.pack(pady=10)

            pop.mainloop()

    def calculate_on_enter(self, event):
        self.calculate()

    def is_weak(self):
        self.result_label.config(text = "Yes! :)")

GUI()
