import streamlit as st
from datetime import datetime, timedelta, time
import matplotlib.pyplot as plt
import re
import io
import base64
import array
from PIL import Image
from matplotlib.patches import Rectangle







def validate_duration_format(duration_str):
    # Use regular expression to validate HH:MM format for duration
    return re.match(r'^([0-9]|[0-9][0-9]|[1-9][0-9][0-9]+):([0-5]\d)$', duration_str)


def get_days_of_service(bus_number, direction):
    while True:
        try:
            while True:  # Boucle interne pour gérer les jours invalides
                jours_map = {
                    "Monday": 1,
                    "Tuesday": 2,
                    "Wednesday": 3,
                    "Thursday": 4,
                    "Friday": 5,
                    "Saturday": 6,
                    "Sunday": 7
                }

                jours_selectionnes = st.multiselect(f"Circulation day(s) of bus {bus_number} from {direction.replace('>', 'to')} ?", list(jours_map.keys()))
                days = []
                
                for jour in jours_selectionnes:
                    days.append(jours_map[jour])
                days = array.array('I', [jours_map[jour] for jour in jours_selectionnes])
                days_list = list(days) 
                if not days:  # Check if the input is empty
                    days_list = []
                    break

                if any(int(day) > 7 for day in days_list):
                    print("Veuillez entrer des jours valides (de 1 à 7). \n\n")                
                
                else:
                    days_list = [int(day) for day in days_list if int(day) in range(1, 8)]  # Modified to accept days 1 to 7
                    break  # Sort de la boucle interne si l'entrée est valide
            break  # Sort de la boucle principale si l'entrée est valide
        except ValueError:
            print("Veuillez entrer des jours valides séparés par des virgules. \n\n")

    return days_list

def plot_arrow(ax, start, end, color):
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color=color))


def number_buses():
    while True:
        try:
            num_buses = st.sidebar.slider("Number of buses 🚌:", min_value=1, max_value=10, value=1, step=1)
            print("\n")
            return num_buses
        except ValueError:
            print(" Veuillez entrer un nombre valide.")

def graphicage_hlp():
    while True:
        try:
            # Solliciter le choix de l'utilisateur dans la barre latérale
            choice = st.sidebar.radio("How many cities? 🚏", options=[2, 3, 4])
            
            # Vérifier si le choix est valide
            if choice not in [2,3,4]:
                raise ValueError("Invalid choice")
            
            return choice  # Retourne le choix valide
        except ValueError as e:
            st.error("Veuillez choisir '2', '3', '4'. Réessayez.")

widget_counter = 0

def additional_info_optional():
    bus_partner = st.sidebar.text_input(f"🤝 Bus Partner")
    depot = st.sidebar.text_input(f"🏠 Deposit")
     #min_date = datetime.strptime('01/01/2022', '%d/%m/%Y')
    service_number = st.sidebar.text_input("🚍 Service numbers")
    #other = st.sidebar.text_input(f"📝 Comments")
    additional_info = {
        '🤝 Bus Partner': bus_partner,
        '🏠 Deposit': depot,
        'Service numbers': service_number
    }
    return bus_partner, depot, service_number, additional_info




def get_unique_key(name):
    return f"{name}_{hash(name)}"

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{bin_file}">{file_label}</a>'
    return href

def get_image_download_button(buffer, filename):
    """Generate a download button for the image."""
    buffer_str = base64.b64encode(buffer).decode()
    button = f'<button><a href="data:image/png;base64,{buffer_str}" download="{filename}">📥 Download Image</a></button>'
    return button

def table(horaires_trajets, num_buses, days_of_services, colors, bbox):
    table_cell = [['' for _ in range(len(horaires_trajets) + 1)] for _ in range(num_buses + 1)]
    table_colors = [['black' for _ in range(len(horaires_trajets) + 1)] for _ in range(num_buses + 1)]
    
    # Populate headers
    headers = list(horaires_trajets.keys())
    table_cell[0][1:] = headers

    # Populate table data and colors
    for i in range(num_buses):
        table_cell[i + 1][0] = f'Bus {i + 1}'
        for j, key in enumerate(headers):
            days_services = ''
            for d in days_of_services.get((i + 1, key), ''):
                days_services = days_services + str(d) + ' '
            table_cell[i + 1][j + 1] = days_services
            table_colors[i + 1][j + 1] = colors[i]
    
    # Create table
    table = plt.table(cellText=table_cell,
                      cellLoc='center',
                      loc='lower right',
                      bbox=bbox)
    
    # Set cell colors
    for i in range(len(table_cell)):
        for j in range(len(table_cell[i])):
            cell = table[i, j]
            cell_text = table_cell[i][j]
            cell_color = table_colors[i][j]
            cell.get_text().set_color(cell_color)
    
    
    # Set border between first and second row
    for i in range(len(table_cell)):
        for j in range(len(table_cell[i])):
            # Outline the entire first column
            cell = table[i, j]
            cell.set_edgecolor('lightgrey')
            cell.set_linewidth(1)
    
    # Adjust font size
    table.auto_set_font_size(False)  # Disable font size auto-scaling
    table.set_fontsize(9)  # Set the font size manually
    
    # Show plot
    plt.show() 

def table_other_info(additional_info, bbox):
    # Initialize table data and colors
    num_items = len(additional_info)
    table_cell = [['' for _ in range(2 * num_items)]]

    # Populate table data and colors
    for i, (key, value) in enumerate(additional_info.items()):
        if value != '':
            table_cell[0][2*i] = f"{key[1:]} : {value}"

    # Create table
    table = plt.table(cellText=table_cell,
                      cellLoc='left',
                      loc='upper right',
                      bbox=bbox)
    for i in range(len(table_cell)):
        for j in range(len(table_cell[i])):
            cell = table[i, j]
            cell.get_text().set_color('#5f003c')

    

    # Set border between cells
    for cell in table._cells:
        table._cells[cell].set_edgecolor('lightgrey')
        table._cells[cell].set_linewidth(1)

    # Adjust font size
    table.auto_set_font_size(False)  # Disable font size auto-scaling
    table.set_fontsize(14)  # Set the font size manually

    # Hide cell edges
    for cell in table._cells:
        table._cells[cell].set_edgecolor('none')

    # Show plot
    plt.show()

        

def horaires():
    num_villes = graphicage_hlp()
    num_buses = number_buses()
    bus_partner, depot, odc, additional_info = additional_info_optional()

    villes = {}
    horaires_trajets = {}

    st.write("<div style='font-size:30px;'><b> 🚏 Cities </b></div>", unsafe_allow_html=True)
    
    # Entrée des villes
    for i in range(num_villes):
        villes[f"ville_{i+1}"] = st.text_input(f"City {i+1}:")
    
    # Traitement des combinaisons de villes où l'ordre compte
    for i in range(num_villes):
        for j in range(num_villes):
            if i != j:  # S'assurer que la ville de départ et d'arrivée ne sont pas les mêmes
                # Début d'un bloc pour une combinaison de villes
                st.markdown("<hr style='border: 1.5px solid #054752;'>", unsafe_allow_html=True)
                st.subheader(f"🚍 Trip: {villes[f'ville_{i+1}']} ➡ {villes[f'ville_{j+1}']}")
                
                # Heure de départ
                horaire_depart = st.time_input(
                    f"Departure time from {villes[f'ville_{i+1}']} to {villes[f'ville_{j+1}']}:", 
                    value=None,
                    key=get_unique_key(f"departure_{i}_{j}")
                )

                if horaire_depart:
                    # Saisie de la durée
                    st.markdown("### Duration")
                    col1, col2 = st.columns(2)
                    heures = col1.number_input(
                        "Heures:", min_value=0, max_value=50, step=1, 
                        key=get_unique_key(f"heures_{i}_{j}")
                    )
                    minutes = col2.number_input(
                        "Minutes:", min_value=0, max_value=59, step=1, 
                        key=get_unique_key(f"minutes_{i}_{j}")
                    )

                    duree_trajet = f"{heures:02d}:{minutes:02d}"
                    trajet_key = f"{villes[f'ville_{i+1}']} > {villes[f'ville_{j+1}']}"
                    
                    # Sauvegarde du trajet
                    horaires_trajets[trajet_key] = {
                        'villes': f'ville_{i+1}_{j+1}',
                        'depart': horaire_depart.strftime("%H:%M"),
                        'duree': duree_trajet
                    }
                    st.success(f"Travel time recorded: **{duree_trajet}**")

                    # Ajout des départs supplémentaires
                    st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)  # Ligne fine pour distinguer
                    st.markdown("##### Additional Departure Time")
                    add_other_departure = st.checkbox(
                        f"Add additional departure time from {villes[f'ville_{i+1}']} to {villes[f'ville_{j+1}']}?", 
                        key=get_unique_key(f"add_departure_{i}_{j}")
                    )
                    additional_count = 1
                    
                    while add_other_departure:
                        additional_depart = st.time_input(
                            f"Additional departure time from {villes[f'ville_{i+1}']} to {villes[f'ville_{j+1}']}:", 
                            key=get_unique_key(f"additional_departure_{i}_{j}_{additional_count}")
                        )
                        
                        # Ajout de l'heure et de la durée supplémentaires pour le même trajet
                        additional_key = f"{trajet_key}_H{additional_count+1}"
                        horaires_trajets[additional_key] = {
                            'villes': f'ville_{i+1}_{j+1}',
                            'depart': additional_depart.strftime("%H:%M"),
                            'duree': duree_trajet
                        }

                        # Nouvelle ligne fine entre horaires
                        st.markdown("<hr style='border: 1px dashed #ccc;'>", unsafe_allow_html=True)
                        add_other_departure = st.checkbox(
                            f"Add another departure time #{additional_count + 1}?",
                            value=False, 
                            key=get_unique_key(f"add_another_departure_{i}_{j}_{additional_count}")
                        )
                        additional_count += 1

                else:
                    st.warning(f"Departure time for {villes[f'ville_{i+1}']} ➡ {villes[f'ville_{j+1}']} not provided")

    return horaires_trajets, num_buses, num_villes, villes, additional_info

def get_days_of_service_all_buses():

    horaires_trajets, num_buses, num_villes, villes, additional_info = horaires()
    days_of_service_villes = {}
    departs_villes = {}
    arrivees_villes = {}
    directions = [key for key, value in horaires_trajets.items()]
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'pink', 'brown']
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thirsday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
    midnight_dates = []
    
    dates_noon = []
    start_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    start_date += timedelta(days=(7 - start_date.weekday()))  # Pour obtenir le prochain lundi
    dates = [start_date + timedelta(days=i) for i in range(8)]  # Générer jusqu'au jour 8 inclus
    
    for date in dates:
        midnight_dates.append(date.replace(hour=0, minute=0, second=0, microsecond=0))
        dates_noon.append(date.replace(hour=12, minute=0, second=0, microsecond=0))
    
    
    days_of_services = {}
    for i in range(num_buses):
        for key, value in horaires_trajets.items():
            if value['depart'] == '':
                days_of_services[(i+1, key)] = ''
            else:
                days_of_services[(i+1, key)] = get_days_of_service(i+1, key)
    days_of_service_villes = {}

    for i in range(num_buses):
        for j in range(num_villes):
            for key, value in horaires_trajets.items():
                direction = key
                days_of_service_villes[(i+1, j+1, direction)] = days_of_services[(i+1, direction)] 
                departs_villes[(i+1, j+1, direction, value['villes'])] = [date for k, date in enumerate(dates) if (k + 1) in days_of_service_villes[(i+1, j+1, direction)]] if days_of_service_villes[(i+1, j+1, direction)] else ''
                arrivees_villes[(i+1, j+1, direction, value['villes'])] = [date for k, date in enumerate(dates) if (k + 1) in days_of_service_villes[(i+1, j+1, direction)]] if days_of_service_villes[(i+1, j+1, direction)] else ''
    
    for key, value in horaires_trajets.items():
        for k, v in departs_villes.items():
            if key == k[2]:
                if value['depart'] != '':
                    try:
                        heure_depart, minutes_depart = map(int, value['depart'].split(':'))
                    except AttributeError:
                        heure_depart = value['depart'].hour
                        minutes_depart = value['depart'].minute               
                    for i in range(len(departs_villes[k])):
                        departs_villes[k][i] = departs_villes[k][i].replace(hour=heure_depart, minute=minutes_depart)

    for key, value in horaires_trajets.items():
        for k, v in departs_villes.items():
            if key == k[2]:
                if value['depart'] != '':
                    try:
                        heure_depart, minutes_depart = map(int, value['depart'].split(':'))
                    except AttributeError:
                        heure_depart = value['depart'].hour
                        minutes_depart = value['depart'].minute               

    for key, value in horaires_trajets.items():
        for k, v in departs_villes.items():
            if key == k[2]:
                if value['depart'] != '':
                    try:
                        heure_duree, minutes_duree = map(int, value['duree'].split(':'))
                    except AttributeError:
                        heure_duree= value['duree'].hour
                        minutes_duree = value['duree'].minute               

                for i in range(len(arrivees_villes[k])):
                    arrivees_villes[k][i] = departs_villes[k][i] + timedelta(hours=heure_duree, minutes=minutes_duree)

                    
    if st.button("Submit"):
                           
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'pink', 'brown', 'yellow', 'turquoise', 'lavender']
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
        midnight_dates = []
        
        dates_noon = []
        start_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        start_date += timedelta(days=(7 - start_date.weekday()))  # Pour obtenir le prochain lundi
        dates = [start_date + timedelta(days=i) for i in range(10)]  
        for date in dates:
            midnight_dates.append(date.replace(hour=0, minute=0, second=0, microsecond=0))
            dates_noon.append(date.replace(hour=12, minute=0, second=0, microsecond=0))
        

        if num_villes == 2:
            fig, ax = plt.subplots(figsize=(20, 15))
            
            for key, value in arrivees_villes.items():
                if key[3] == 'ville_2_1':
                    if key[1] == 1:
                        for i in range(len(arrivees_villes[key])):
                            if departs_villes[key] != '':
                                ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                                ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                                #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                                #ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                                plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 1), colors[key[0]-1])

                                for i, time in enumerate(departs_villes[key]):
                                    ax.annotate(f"{time.strftime('%H:%M')}",
                                                (time, -1.07),
                                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                                for i, time in enumerate(arrivees_villes[key]):
                                    ax.annotate(f"{time.strftime('%H:%M')}",
                                                (time, 1.01),
                                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)

                if key[3] == 'ville_1_2': 
                    for i in range(len(arrivees_villes[key])):
                        if departs_villes[key] != '':
                            ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                            ax.scatter(departs_villes[key], [1]*len(departs_villes[key]),  color=colors[key[0]-1])
                            #ax.plot([arrivees_villes[key], arrivees_villes[key]], [1, -1], linestyle='dotted', color='grey', alpha=0.5)
                            #ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                            plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], -1), colors[key[0]-1])
                            for i, time in enumerate(departs_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                            (time, 1.03),
                                            textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                            for i, time in enumerate(arrivees_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                            (time, -1.0),
                                            textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
            

            for date in midnight_dates:
                ax.plot([date, date], [-1, 1], color='lightblue', linestyle='-', linewidth=1)
            

            plt.yticks([-1, 1], [ f"{villes['ville_2']}", f"{villes['ville_1']}"], fontsize=20)
            plt.yticks([-1, 1], [f"{villes['ville_2']}", f"{villes['ville_1']}"], fontsize=20, color = '#054752')
            plt.xticks(dates_noon, [days_of_week[date.weekday()] for date in dates], fontsize=20, ha='center', va='center', color = '#054752')
            plt.tick_params(axis='x', which='both', bottom=False, top=True, labelbottom=False, labeltop=True, colors='#054752')
            plt.gca().xaxis.set_tick_params(pad=-30)
            x_min, x_max = plt.xlim()
            y_min, y_max = plt.ylim()
            rect_x = x_min - 0.05
            rect_y = y_min - 0.05
            rect_width = x_max - x_min +0.1
            rect_height = y_max - y_min +0.1

            # Draw the rectangle around the xtick labels
            plt.gca().add_patch(plt.Rectangle((rect_x, rect_y), rect_width, rect_height, fill=False, edgecolor='#054752'))

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.set_xlim(midnight_dates[0], midnight_dates[-2])
            ax.set_ylim(-2, 1.4)
            title_color = 'coral'
            plt.title(f"Graphicage {villes['ville_1']} - {villes['ville_2']}", y=1.08, color=title_color, fontsize=20)
            title_obj = plt.gca().title
            title_obj.set_bbox(dict(facecolor='white', edgecolor='coral', boxstyle='round,pad=0.8'))

            length_unit = 0.15
            width_unit = 0.03
            x = 0
            y = 0

            bbox = [x,y,length_unit*(len(horaires_trajets.keys())+1),width_unit*(num_buses+1)]
            table(horaires_trajets, num_buses, days_of_services, colors, bbox)
            bbox = [x+0.05,y+0.99,1.1,0.1]
            table_other_info(additional_info, bbox)
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            filename = f"Graphicage {villes['ville_1']} - {villes['ville_2']}.png"  # Define the filename for the graph image
            image_bytes = buffer.getvalue()
            st.markdown(get_image_download_button(image_bytes, filename=filename), unsafe_allow_html=True)
            st.image(buffer, use_column_width=True)
            fig.set_size_inches(20*0.5, 15*0.5)
            plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.3)
            plt.savefig(f"Graphicage {villes['ville_1']} - {villes['ville_2']}.png", bbox_inches='tight')
            plt.close()

            

        if num_villes == 3:
            fig, ax = plt.subplots(figsize=(20, 15))  
            
            for key, value in arrivees_villes.items():
                if key[3] == 'ville_3_2':
                    if key[1] == 1:
                        for i in range(len(arrivees_villes[key])):
                            if departs_villes[key] != '':
                                ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                                ax.scatter(departs_villes[key], [0]*len(departs_villes[key]),  color=colors[key[0]-1])
                                #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                                #ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                                plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 0), colors[key[0]-1])

                                for i, time in enumerate(departs_villes[key]):
                                    ax.annotate(f"{time.strftime('%H:%M')}",
                                                (time, -1.07),
                                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                                for i, time in enumerate(arrivees_villes[key]):
                                    ax.annotate(f"{time.strftime('%H:%M')}",
                                                (time, 1.01),
                                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)

                if key[3] == 'ville_2_3':
                    if value != '':
                        ax.scatter(departs_villes[key], [0]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 0), (arrivees_villes[key][i], -1), colors[key[0]-1])

                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 0.02),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -0.98),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)


                if key[3] == 'ville_3_1':
                    if value != '':
                        ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 1), colors[key[0]-1])
                    

                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1.06),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, 1.1),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
            
                if key[3] == 'ville_1_3':
                    if value != '':
                        ax.scatter(departs_villes[key], [1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], -1), colors[key[0]-1])

                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1.04),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -1.03),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)

                if key[3] == 'ville_2_1':
                        if value != '':
                            ax.scatter(departs_villes[key], [0]*len(departs_villes[key]),  color=colors[key[0]-1])
                            #ax.plot([departs_villes[key], departs_villes[key]], [0, 1], linestyle='dotted', color='grey', alpha=0.5)
                            ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                            #ax.plot([arrivees_villes[key], arrivees_villes[key]], [0, 1], linestyle='dotted', color='grey', alpha=0.5)
                            for i in range(len(departs_villes[key])):
                                plot_arrow(ax, (departs_villes[key][i], 0), (arrivees_villes[key][i], 1), colors[key[0]-1])
                        

                            for i, time in enumerate(departs_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                            (time, -0.07),
                                    textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                            
                            for i, time in enumerate(arrivees_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                    (time, 1.1),
                                    textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)

                if key[3] == 'ville_1_2':

                    
                    if value != '':

                        ax.scatter(departs_villes[key], [1]*len(departs_villes[key]),  color=colors[key[0]-1])

                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [0]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], 0), colors[key[0]-1])


                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1.03),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -0.01),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)


            for date in midnight_dates:
                ax.plot([date, date], [-1, 1], color='lightblue', linestyle='-', linewidth=1)
            
            plt.yticks([-1, 0, 1], [f"{villes['ville_3']}", f"{villes['ville_2']}", f"{villes['ville_1']}"], fontsize=20, color = '#054752')
            
            plt.xticks(dates_noon, [days_of_week[date.weekday()] for date in dates], fontsize=20, ha='center', va='center', color = '#054752')
            plt.tick_params(axis='x', which='both', bottom=False, top=True, labelbottom=False, labeltop=True, colors='#054752')
            plt.gca().xaxis.set_tick_params(pad=-30)
            x_min, x_max = plt.xlim()
            y_min, y_max = plt.ylim()
            rect_x = x_min - 0.05
            rect_y = y_min - 0.05
            rect_width = x_max - x_min +0.1
            rect_height = y_max - y_min +0.1

            # Draw the rectangle around the xtick labels
            plt.gca().add_patch(plt.Rectangle((rect_x, rect_y), rect_width, rect_height, fill=False, edgecolor='#054752'))

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.set_xlim(midnight_dates[0], midnight_dates[-2])
            ax.set_ylim(-2, 1.6)
            title_color = 'coral'
            plt.title(f"Graphicage {villes['ville_3']} - {villes['ville_2']} - {villes['ville_1']}", y=1.08, color=title_color, fontsize=20)
            title_obj = plt.gca().title
            title_obj.set_bbox(dict(facecolor='white', edgecolor='coral', boxstyle='round,pad=0.8'))

            length_unit = 0.15
            width_unit = 0.03
            x = 0
            y = 0
            bbox = [x,y,length_unit*(len(horaires_trajets.keys())+1),width_unit*(num_buses+1)]
            table(horaires_trajets, num_buses, days_of_services, colors, bbox)
            bbox = [x+0.05,y+0.99,1,0.1]
            table_other_info(additional_info, bbox)
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            filename = f"Graphicage {villes['ville_1']} - {villes['ville_2']} -  {villes['ville_3']}.png"  # Define the filename for the graph image
            image_bytes = buffer.getvalue()
            st.markdown(get_image_download_button(image_bytes, filename=filename), unsafe_allow_html=True)
            st.image(buffer, use_column_width=True)
            fig.set_size_inches(20*0.5, 15*0.5)
            plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.3)
            plt.savefig(f"Graphicage {villes['ville_1']} - {villes['ville_2']} -  {villes['ville_3']}.png", bbox_inches='tight')
            plt.close()

        if num_villes == 4:
            fig, ax = plt.subplots(figsize=(20, 15))
            for key in departs_villes.keys():
                print("key")
                print(key)
                  
               
            # Afficher la première valeur des clés contenant cet élément
            for key, value in departs_villes.items():

                if key[3] == 'ville_3_2':
                    if value != '':
                        ax.scatter(departs_villes[key], [-1/3]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [1/3]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], -1/3), (arrivees_villes[key][i], 1/3), colors[key[0]-1])
                    
                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1/3 + 0.02),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, 1/3 + 0.01),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)


                if key[3] == 'ville_2_3':
                    if value != '':
                        ax.scatter(departs_villes[key], [1/3]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1/3]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 1/3), (arrivees_villes[key][i], -1/3), colors[key[0]-1])

                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1/3+0.02),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -1/3+0.02),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)


                if key[3] == 'ville_3_1':
                    if value != '':
                        ax.scatter(departs_villes[key], [-1/3]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], -1/3), (arrivees_villes[key][i], 1), colors[key[0]-1])
                    

                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1/3-0.06),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, 1+0.1),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
            
                if key[3] == 'ville_3_2':
                    if value != '':
                        ax.scatter(departs_villes[key], [1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1/3]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], -1/3), colors[key[0]-1])

                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1.04),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -1/3 + 0.03),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)

                if key[3] == 'ville_2_1':
                        if value != '':
                            ax.scatter(departs_villes[key], [1/3]*len(departs_villes[key]),  color=colors[key[0]-1])
                            #ax.plot([departs_villes[key], departs_villes[key]], [0, 1], linestyle='dotted', color='grey', alpha=0.5)
                            ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                            #ax.plot([arrivees_villes[key], arrivees_villes[key]], [0, 1], linestyle='dotted', color='grey', alpha=0.5)
                            for i in range(len(departs_villes[key])):
                                plot_arrow(ax, (departs_villes[key][i], 1/3), (arrivees_villes[key][i], 1), colors[key[0]-1])
                        

                            for i, time in enumerate(departs_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                            (time, 1/3 -0.07),
                                    textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                            
                            for i, time in enumerate(arrivees_villes[key]):
                                ax.annotate(f"{time.strftime('%H:%M')}",
                                    (time, 1.1),
                                    textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)

                if key[3] == 'ville_1_2':
                    
                    if value != '':
                        ax.scatter(departs_villes[key], [1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [1/3]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], 1/3), colors[key[0]-1])


                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1.03),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, 1/3 - 0.01),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
                
                if key[3] == 'ville_4_1':
                    
                    if value != '':
                        ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 1), colors[key[0]-1])


                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1.05),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, 1 + 0.05),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)

                if key[3] == 'ville_1_4':
                    if value != '':
                        ax.scatter(departs_villes[key], [1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 1), (arrivees_villes[key][i], -1), colors[key[0]-1])


                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1.02),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -1 + 0.02),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
                        
                if key[3] == 'ville_2_4':
                    
                    if value != '':
                        ax.scatter(departs_villes[key], [1/3]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], 1/3), (arrivees_villes[key][i], -1), colors[key[0]-1])


                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, 1/3+0.01),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -1 - 0.01),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
                            
                if key[3] == 'ville_4_2':
                    
                    if value != '':
                        ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [1/3]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], 1/3), colors[key[0]-1])


                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1 - 0.05),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, 1/3 + 0.03),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
                            
                if key[3] == 'ville_3_4':
                    
                    if value != '':
                        ax.scatter(departs_villes[key], [-1/3]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], -1/3), (arrivees_villes[key][i], -1), colors[key[0]-1])


                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1/3+0.01),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -1 - 0.01),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)
                            
                if key[3] == 'ville_4_3':
                    
                    if value != '':
                        ax.scatter(departs_villes[key], [-1]*len(departs_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([departs_villes[key], departs_villes[key]], [-1, 0], linestyle='dotted', color='grey', alpha=0.5)
                        ax.scatter(arrivees_villes[key], [-1/3]*len(arrivees_villes[key]),  color=colors[key[0]-1])
                        #ax.plot([arrivees_villes[key], arrivees_villes[key]], [-1, 1], linestyle='dotted', color='grey', alpha=0.5)
                        for i in range(len(departs_villes[key])):
                            plot_arrow(ax, (departs_villes[key][i], -1), (arrivees_villes[key][i], -1/3), colors[key[0]-1])


                        for i, time in enumerate(departs_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                        (time, -1-0.05),
                                textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)
                        
                        for i, time in enumerate(arrivees_villes[key]):
                            ax.annotate(f"{time.strftime('%H:%M')}",
                                (time, -1/3 + 0.03),
                                textcoords="offset points", xytext=(0, -20), ha='center', fontsize=8)

            for date in midnight_dates:
                ax.plot([date, date], [-1, 1], color='lightblue', linestyle='-', linewidth=1)
            
            plt.yticks([-1, -1/3, 1/3, 1], [f"{villes['ville_4']}", f"{villes['ville_3']}", f"{villes['ville_2']}", f"{villes['ville_1']}"], fontsize=20, color = '#054752')
            
            plt.xticks(dates_noon, [days_of_week[date.weekday()] for date in dates], fontsize=20, ha='center', va='center', color = '#054752')
            plt.tick_params(axis='x', which='both', bottom=False, top=True, labelbottom=False, labeltop=True, colors='#054752')
            plt.gca().xaxis.set_tick_params(pad=-30)
            x_min, x_max = plt.xlim()
            y_min, y_max = plt.ylim()
            rect_x = x_min - 0.05
            rect_y = y_min - 0.05
            rect_width = x_max - x_min +0.1
            rect_height = y_max - y_min +0.1

            # Draw the rectangle around the xtick labels
            plt.gca().add_patch(plt.Rectangle((rect_x, rect_y), rect_width, rect_height, fill=False, edgecolor='#054752'))

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.set_xlim(midnight_dates[0], midnight_dates[-2])
            ax.set_ylim(-2, 1.6)
            title_color = 'coral'
            plt.title(f"Graphicage {villes['ville_4']}, {villes['ville_3']} - {villes['ville_2']} - {villes['ville_1']}", y=1.08, color=title_color, fontsize=20)
            title_obj = plt.gca().title
            title_obj.set_bbox(dict(facecolor='white', edgecolor='coral', boxstyle='round,pad=0.8'))

            length_unit = 0.11
            width_unit = 0.03
            x = -0.16
            y = 0
            bbox = [x,y,length_unit*(len(horaires_trajets.keys())+1),width_unit*(num_buses+1)]
            table(horaires_trajets, num_buses, days_of_services, colors, bbox)
            bbox = [x+0.05,y+0.99,1,0.1]
            table_other_info(additional_info, bbox)
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            filename = f"Graphicage {villes['ville_1']} - {villes['ville_2']} -  {villes['ville_3']} -  {villes['ville_4']}.png"  # Define the filename for the graph image
            image_bytes = buffer.getvalue()
            st.markdown(get_image_download_button(image_bytes, filename=filename), unsafe_allow_html=True)
            st.image(buffer, use_column_width=True)
            fig.set_size_inches(20*0.5, 15*0.5)
            plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.3)
            plt.savefig(f"Graphicage {villes['ville_1']} - {villes['ville_2']} -  {villes['ville_3']} -  {villes['ville_4']}.png", bbox_inches='tight')
            plt.close()
    


if __name__ == '__main__':
    get_days_of_service_all_buses()
