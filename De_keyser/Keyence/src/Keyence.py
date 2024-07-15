import os
import numpy as np
import datetime

def trace(message):
    print("kf_trace: " + str(message))

def on_press(key):
    pass

def Lees_AllKeyS(client):
# leest alle Keyence sensoren na elkaar uit
    data="MS\r\n"
    data=data.encode("utf8")
    client.send(data)

    Antwoord = client.recv(1024)
    KeyS_1 = int(Antwoord[6:16])/1000
    KeyS_2 = int(Antwoord[20:30])/1000
    KeyS_3 = int(Antwoord[34:44])/1000

    return KeyS_1,KeyS_2,KeyS_3

# Fix offset sensoren in geval van lege conveyor band
def FOSen(AlleSensoren, offsetsensoren):
    trace('zero all sensors')
    offsetsensoren = AlleSensoren
    return offsetsensoren

def maak_nieuwe_mappen():
    # Krijg de huidige datum
    datum = datetime.datetime.now().strftime("%Y-%m-%d")

    # Bepaal de gewenste hoofdmap
    # hoofdmap = r"C:\Users\Keynce\Documents\CSV_Keyence"
    hoofdmap = r"C:\Users\andre\Desktop\De Keyser\Keyence\code\venv\CSV_Keyence"

    # Creëer de mapnamen
    mapnaam_csv = os.path.join(hoofdmap, f"CSV_{datum}")
    mapnaam_plots = os.path.join(hoofdmap, f"Plots_{datum}")
    mapnaam_Scheldiktes = os.path.join(hoofdmap, f"Scheldiktes_{datum}")

    # Controleer of de mappen al bestaan, zo niet, maak ze dan aan
    if not os.path.exists(mapnaam_csv):
        os.makedirs(mapnaam_csv)
        print(f"Map '{mapnaam_csv}' is aangemaakt.")

    if not os.path.exists(mapnaam_plots):
        os.makedirs(mapnaam_plots)
        print(f"Map '{mapnaam_plots}' is aangemaakt.")
        
    if not os.path.exists(mapnaam_Scheldiktes):
        os.makedirs(mapnaam_Scheldiktes)
        print(f"Map '{mapnaam_Scheldiktes}' is aangemaakt.")

        # Maak submappen aan binnen de map 'minima_<datum>'
        for i in range(1, 4):
            submap_naam = os.path.join(mapnaam_Scheldiktes, f"Scheldiktes_spoor{i}")
            os.makedirs(submap_naam)
            print(f"Submap '{submap_naam}' is aangemaakt.")

def find_max_min_indices(values_filtered, derivative, threshold_derivative):
    max_indices = []
    min_indices = []

    # Itereer over de waarden van values_filtered en vind de indexpunten van de maxima en minima van de eerste afgeleide
    for i in range(1, len(values_filtered) - 1):
        if derivative[i] > threshold_derivative and derivative[i] > derivative[i - 1] and derivative[i] > derivative[i + 1]:
            max_indices.append(i)
        elif derivative[i] < -threshold_derivative and derivative[i] < derivative[i - 1] and derivative[i] < derivative[i + 1]:
            min_indices.append(i)

    # Itereer over de maximale indices
    i = 0
    while i < len(max_indices) - 1:
        max_index = max_indices[i]
        next_max_index = max_indices[i + 1]

        # Controleer of er een minimale index tussen zit
        min_between = False
        for min_index in min_indices:
            if max_index < min_index < next_max_index:
                min_between = True
                break

        # Als er geen minimale index tussen zit, verwijder de tweede maximale index
        if not min_between:
            del max_indices[i + 1]
        else:
            i += 1

    # Itereer over de minimum indices
    i_1 = 0
    while i_1 < len(min_indices) - 1:
        min_index_1 = min_indices[i_1]
        next_min_index_1 = min_indices[i_1 + 1]

        # Controleer of er een maximale index tussen zit
        max_between_1 = False
        for max_index_1 in max_indices:
            if min_index_1 < max_index_1 < next_min_index_1:
                max_between_1 = True
                break

        # Als er geen maximale index tussen zit, verwijder de eerste minimale index
        if not max_between_1:
            del min_indices[i_1]
        else:
            i_1 += 1

    return max_indices, min_indices

def find_peaks(max_indices, min_indices, values_filtered):
    # Lijst om de pieken op te slaan als tuples van (index, waarde)
    peaks = []

    # Voeg maximale indices en corresponderende waarden toe aan de lijst
    for max_index in max_indices:
        peaks.append((max_index, values_filtered[max_index]))

    # Voeg minimale indices en corresponderende waarden toe aan de lijst
    for min_index in min_indices:
        peaks.append((min_index, values_filtered[min_index]))

    # Sorteer de lijst met pieken op basis van index
    peaks.sort(key=lambda x: x[0])

    # Lijst om alleen de waarden van de pieken op te slaan
    peak_values = [peak[1] for peak in peaks]

    return peak_values

def extract_values_between_peaks(max_indices, min_indices, values_filtered):
    waarden_tussen_pieken_lijsten = []
    waarden_tussen_pieken_lijsten_all = []

    if not max_indices or not min_indices:
        return waarden_tussen_pieken_lijsten, []

    for start_index_1, end_index_1 in zip(max_indices, min_indices):
        waarden_tussen_pieken = values_filtered[start_index_1 + 1:end_index_1]

        waarden_tussen_pieken_lijst = waarden_tussen_pieken[2:-2]
        waarden_tussen_pieken_lijst_all = waarden_tussen_pieken

        if len(waarden_tussen_pieken_lijst) > 0:  # Controleer of de lijst niet leeg is
            waarden_tussen_pieken_lijsten.append(waarden_tussen_pieken_lijst)
        waarden_tussen_pieken_lijsten_all.append(waarden_tussen_pieken_lijst_all)

    waarden_tussen_pieken_lijsten_flat = np.concatenate(waarden_tussen_pieken_lijsten_all).tolist()

    return waarden_tussen_pieken_lijsten, waarden_tussen_pieken_lijsten_flat

def bereken_avg_tussen(values_filtered, gemiddelde_value, waarden_tussen_pieken_lijsten_flat, piekwaarden):
    nul_gemiddelden = [x for x in values_filtered if x <= gemiddelde_value]
    nul_gemiddelden_2 = [x for x in nul_gemiddelden if x not in waarden_tussen_pieken_lijsten_flat]
    nul_gemiddelden_3 = nul_gemiddelden_2.copy()

    for waarde in piekwaarden:
        if waarde in nul_gemiddelden_3:
            nul_gemiddelden_3.remove(waarde)

    if len(nul_gemiddelden_3) == 0:  # Als de lijst leeg is, return 0 om deling door nul te voorkomen
        return 0

    avg_tussen = round(sum(nul_gemiddelden_3) / len(nul_gemiddelden_3), 2)
    return avg_tussen

def bereken_scheldiktes(waarden_tussen_pieken_lijsten_, avg_tussen):
    # Lijst om scheldiktes op te slaan
    scheldiktes = []

    # Loop door de lijsten met waarden tussen de pieken
    for waarden_tussen_pieken_lijst_ in waarden_tussen_pieken_lijsten_:
        # Vind de kleinste waarde in de huidige lijst
        kleinste_waarde_ = min(waarden_tussen_pieken_lijst_)

        # Trek de waarde avg_onderAVG_Y1 af van de kleinste waarde
        scheldikte_ = kleinste_waarde_ - avg_tussen

        # Voeg de resulterende waarde toe aan de lijst scheldiktes
        scheldiktes.append(scheldikte_)

    # Afronden van de waarden in scheldiktes1 op 2 decimalen
    scheldiktes_rounded = [round(scheldikte, 2) for scheldikte in scheldiktes]

    return scheldiktes_rounded

def update_subplot(ax, values_filtered, max_indices, min_indices, gemiddelde_value, avg_nullijn, title, label):
    ax.set_ylabel('Dikte vd schel')
    ax.set_title(title)
    ax.plot(values_filtered, color='blue')  # Pas de kleur aan indien nodig
    for start, end in zip(max_indices, min_indices):
        ax.vlines(x=start, ymin=-2, ymax=7, color='green', linestyle='--')
        ax.vlines(x=end, ymin=-2, ymax=7, color='black', linestyle='--')
    ax.axhline(y=gemiddelde_value, color='red', linestyle='--')
    ax.axhline(y=avg_nullijn, color='black', linestyle='--', label=f'{label}: {avg_nullijn}')
    ax.legend(loc='center left', bbox_to_anchor=(0.90, 1.30))

def plot_histogram(ax, data_filtered, mean, std_dev, title, count_text_good, count_text_bad, spoor):
    ax.hist(data_filtered, bins=10)
    ax.set_ylabel('Frequentie')
    ax.set_xlabel('Dikte v/d schel')
    ax.set_title(title, pad=17)
    ax.axvline(x=mean - std_dev, color='r', linestyle='--')
    ax.axvline(x=mean + std_dev, color='r', linestyle='--')
    ax.axvline(x=mean, color='k', linestyle='-', linewidth=1.5, label=f"Gemiddelde: {mean:.2f}")
    counts, edges, _ = ax.hist(data_filtered, bins=10)
    ymax = np.max(counts)
    ax.text(mean + 0.004, ymax * 1.06, f'Gm: {mean:.2f}', color='k', ha='left')

    std_dev_str = f"Sd: {std_dev:.2f}"
    ax.legend([std_dev_str], fontsize='7')

    # Bepaal de positie en grootte van de rechthoek voor goede schellen
    bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white")

    x_pos_good = -0.3
    y_pos_good = -0.75

    # Teken de rechthoek met het aantal goede schellen
    ax.text(x_pos_good, y_pos_good, count_text_good, transform=ax.transAxes, bbox=bbox_props)

    # Bepaal de positie en grootte van de rechthoek voor slechte schellen
    bbox_props_bad = dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white")

    x_pos_bad = x_pos_good + 0.9
    y_pos_bad = -0.75
    # Teken de rechthoek met het aantal slechte schellen
    ax.text(x_pos_bad, y_pos_bad, count_text_bad, transform=ax.transAxes, bbox=bbox_props_bad)

def show_plot(app, fig):
    fig.show()
    app.exec_()
    
def extract_datetime(file_path):
    return "_".join(os.path.splitext(os.path.basename(file_path))[0].split("_")[-2:])
