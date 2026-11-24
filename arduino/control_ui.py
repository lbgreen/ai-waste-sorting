"""Manual serial control for arduino/sorter_test/sorter_test.ino."""

import tkinter as tk
from tkinter import messagebox, ttk

import serial
from serial.tools import list_ports


BAUD = 9600
STEPS_PER_REV = 2048


class ControlWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Flap-Test")
        self.port = None
        self.buffer = b""
        self.ready = False
        self.busy = False
        self.steps = None
        self.error_pending = False

        self.port_name = tk.StringVar()
        self.zero_confirmed = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Nicht verbunden")
        self.angle1 = tk.StringVar(value="—")
        self.angle2 = tk.StringVar(value="—")
        self.motion_buttons = []
        self.sort_buttons = []

        frame = ttk.Frame(root, padding=16)
        frame.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)

        connection = ttk.LabelFrame(frame, text="Verbindung", padding=10)
        connection.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        connection.columnconfigure(0, weight=1)
        self.port_menu = ttk.Combobox(connection, textvariable=self.port_name, state="readonly", width=30)
        self.port_menu.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ttk.Button(connection, text="Ports suchen", command=self.refresh_ports).grid(row=0, column=1, padx=3)
        self.connect_button = ttk.Button(connection, text="Verbinden", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=2, padx=(3, 0))
        ttk.Label(connection, textvariable=self.status).grid(row=1, column=0, columnspan=3, sticky="w", pady=(8, 0))

        position = ttk.LabelFrame(frame, text="Position (aus Schritten geschätzt)", padding=10)
        position.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        position.columnconfigure(1, weight=1)
        ttk.Label(position, text="Flap 1").grid(row=0, column=0, sticky="w", padx=(0, 15))
        ttk.Label(position, textvariable=self.angle1, font=("TkDefaultFont", 18, "bold")).grid(
            row=0, column=1, sticky="w"
        )
        ttk.Label(position, text="Flap 2").grid(row=1, column=0, sticky="w", padx=(0, 15))
        ttk.Label(position, textvariable=self.angle2, font=("TkDefaultFont", 18, "bold")).grid(
            row=1, column=1, sticky="w"
        )
        self.reference_check = ttk.Checkbutton(
            position,
            text="Startlage beider Flaps bei 0° geprüft",
            variable=self.zero_confirmed,
            command=self.update_controls,
        )
        self.reference_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        sorting = ttk.LabelFrame(frame, text="Sortierablauf (startet nur bei 0° / 0°)", padding=10)
        sorting.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        for col, (label, command) in enumerate(
            (("Paper", "P"), ("Recycling", "R"), ("General", "G"))
        ):
            button = ttk.Button(sorting, text=label, command=lambda c=command: self.send(c))
            button.grid(row=0, column=col, padx=3)
            self.motion_buttons.append(button)
            self.sort_buttons.append(button)

        manual = ttk.LabelFrame(frame, text="Flaps einzeln", padding=10)
        manual.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(manual, text="Flap 1").grid(row=0, column=0, sticky="w")
        ttk.Label(manual, text="Flap 2").grid(row=1, column=0, sticky="w")
        rows = (
            ((+90, "1"), (-90, "2"), (0, "0"), ("+ Schritt", "+"), ("− Schritt", "-")),
            (("Offen", "3"), ("Zu / 0°", "4"), ("+ Schritt", ">"), ("− Schritt", "<")),
        )
        for row, entries in enumerate(rows):
            for col, (label, command) in enumerate(entries, start=1):
                button = ttk.Button(manual, text=str(label), command=lambda c=command: self.send(c))
                button.grid(row=row, column=col, padx=3, pady=3)
                self.motion_buttons.append(button)

        reference = ttk.LabelFrame(frame, text="Nullpunkt setzen", padding=10)
        reference.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(
            reference,
            text="Nur drücken, wenn die betreffende Klappe tatsächlich in der 0°-Stellung steht.",
            wraplength=560,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        for col, (label, command) in enumerate((("Flap 1 = 0°", "Z"), ("Flap 2 = 0°", "X"))):
            button = ttk.Button(reference, text=label, command=lambda c=command: self.send(c))
            button.grid(row=1, column=col, padx=3)
            self.motion_buttons.append(button)

        self.stop_button = ttk.Button(frame, text="Stopp", command=self.stop)
        self.stop_button.grid(row=5, column=0, sticky="ew")
        ttk.Label(
            frame,
            text="Stopp beendet die Schrittfolge. Die Winkel sind keine Sensormesswerte.",
            wraplength=560,
        ).grid(row=6, column=0, sticky="w", pady=(8, 0))

        self.refresh_ports()
        self.update_controls()
        root.after(40, self.poll_serial)
        root.protocol("WM_DELETE_WINDOW", self.close)

    def refresh_ports(self):
        ports = [item.device for item in list_ports.comports()]
        self.port_menu["values"] = ports
        if self.port_name.get() not in ports:
            self.port_name.set(ports[0] if ports else "")

    def toggle_connection(self):
        if self.port is not None:
            self.disconnect()
            return
        name = self.port_name.get()
        if not name:
            self.status.set("Kein serieller Port gefunden")
            return
        try:
            self.port = serial.Serial(name, BAUD, timeout=0, write_timeout=0.5)
        except (serial.SerialException, OSError) as exc:
            messagebox.showerror("Verbindung fehlgeschlagen", str(exc))
            return
        self.buffer = b""
        self.ready = False
        self.busy = False
        self.steps = None
        self.zero_confirmed.set(False)
        self.angle1.set("—")
        self.angle2.set("—")
        self.status.set("Verbunden; warte auf Arduino-Neustart …")
        self.update_controls()
        self.root.after(2000, self.query_position)

    def query_position(self):
        if self.port is not None and not self.ready and not self.busy:
            self.write("?")

    def write(self, command: str):
        try:
            self.port.write(command.encode("ascii"))
            return True
        except (serial.SerialException, OSError) as exc:
            self.disconnect(f"Verbindung verloren: {exc}")
            return False

    def send(self, command: str):
        if (
            self.port is None or not self.ready or self.busy
            or self.steps is None or not self.zero_confirmed.get()
        ):
            return
        if command in "PRG" and self.steps != (0, 0):
            self.status.set("Sortierablauf: beide Flaps zuerst auf 0° fahren")
            return
        if self.write(command):
            self.busy = True
            self.error_pending = False
            self.status.set("Befehl läuft …")
            self.update_controls()

    def stop(self):
        if self.port is not None and self.busy and self.write("!"):
            self.status.set("Stopp angefordert …")

    def poll_serial(self):
        if self.port is not None:
            try:
                count = self.port.in_waiting
                if count:
                    self.buffer += self.port.read(count)
                    if len(self.buffer) > 1024:
                        self.buffer = b""
                        self.status.set("Serielle Meldung zu lang; verworfen")
                    while b"\n" in self.buffer:
                        line, self.buffer = self.buffer.split(b"\n", 1)
                        self.handle_line(line.decode("ascii", errors="replace").strip())
            except (serial.SerialException, OSError) as exc:
                self.disconnect(f"Verbindung verloren: {exc}")
        self.root.after(40, self.poll_serial)

    def handle_line(self, line: str):
        if line == "READY":
            self.ready = True
            self.busy = False
            self.steps = None
            self.error_pending = False
            self.zero_confirmed.set(False)
            self.angle1.set("—")
            self.angle2.set("—")
            self.status.set("Arduino bereit; Startlage 0° prüfen und bestätigen")
        elif line.startswith("POS "):
            parts = line.split()
            if len(parts) != 3:
                return
            try:
                self.steps = (int(parts[1]), int(parts[2]))
            except ValueError:
                return
            self.angle1.set(f"{self.steps[0] * 360 / STEPS_PER_REV:+.1f}°")
            self.angle2.set(f"{self.steps[1] * 360 / STEPS_PER_REV:+.1f}°")
        elif line == "BUSY":
            self.status.set("Bewegung läuft …")
        elif line.startswith("ERROR "):
            self.error_pending = True
            self.status.set(f"Arduino-Fehler: {line[6:]}")
        elif line == "DONE":
            self.busy = False
            if not self.error_pending:
                self.status.set("Bereit")
            self.error_pending = False
        elif line == "STOPPED":
            self.busy = False
            self.status.set("Gestoppt; Position der Flaps prüfen")
        self.update_controls()

    def update_controls(self):
        connected = self.port is not None
        active = (
            connected and self.ready and self.steps is not None
            and self.zero_confirmed.get() and not self.busy
        )
        for button in self.motion_buttons:
            button.configure(state="normal" if active else "disabled")
        for button in self.sort_buttons:
            button.configure(state="normal" if active and self.steps == (0, 0) else "disabled")
        self.stop_button.configure(state="normal" if connected and self.busy else "disabled")
        self.reference_check.configure(
            state="normal" if connected and self.ready and self.steps is not None and not self.busy
            else "disabled"
        )
        self.connect_button.configure(
            text="Trennen" if connected else "Verbinden",
            state="disabled" if self.busy else "normal",
        )

    def disconnect(self, status="Nicht verbunden"):
        if self.port is not None:
            try:
                self.port.close()
            except (serial.SerialException, OSError):
                pass
        self.port = None
        self.ready = False
        self.busy = False
        self.steps = None
        self.zero_confirmed.set(False)
        self.buffer = b""
        self.angle1.set("—")
        self.angle2.set("—")
        self.status.set(status)
        self.update_controls()

    def close(self):
        if self.busy:
            self.stop()
            self.status.set("Stopp angefordert; nach Bestätigung erneut schließen")
            return
        self.disconnect()
        self.root.destroy()


if __name__ == "__main__":
    ControlWindow(tk.Tk()).root.mainloop()
