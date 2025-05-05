from datetime import datetime
from databasemanager import DatabaseManager


class Slides(DatabaseManager):
    MAX_SLIDES = 10

    def __init__(self, db_name):
        super().__init__(db_name)
       
        self.execute('''
            CREATE TABLE IF NOT EXISTS slides (
                id INTEGER PRIMARY KEY,
                name TEXT,
                organ TEXT,
                url TEXT,
                description TEXT)''', commit=True)
        
       
        self.execute('''
            CREATE TABLE IF NOT EXISTS shown_slides (
                slide_id INTEGER,
                user_id INTEGER,  -- إضافة العمود user_id هنا
                shown_date TIMESTAMP,
                FOREIGN KEY (slide_id) REFERENCES slides (id))''', commit=True)

    def add_slide(self, id, name, organ, url, description):
        self.execute('''
            INSERT INTO slides (id, name, organ, url, description)
            VALUES (?, ?, ?, ?, ?)''', (id, name, organ, url, description), commit=True)

    def get_random_slides(self, user_id, n=10):
      
        slide_locations = self.execute('''
            SELECT id, url, name, organ, description FROM slides 
            WHERE id NOT IN (
                SELECT slide_id FROM shown_slides WHERE user_id = ?
            )
            ORDER BY RANDOM()
            LIMIT ?
        ''', (user_id, n), fetch=True)

        
        if not slide_locations:
            
            self.execute('DELETE FROM shown_slides WHERE user_id = ?', (user_id,), commit=True)

            
            slide_locations = self.execute('''
                SELECT id, url, name, organ, description FROM slides 
                ORDER BY RANDOM()
                LIMIT ?
            ''', (n,), fetch=True)

       
        for slide in slide_locations:
            self.execute('''
                INSERT INTO shown_slides (user_id, slide_id, shown_date)
                VALUES (?, ?, ?)
            ''', (user_id, slide[0], datetime.now()), commit=True)

        slide_info =  [
            {
                "id": slide[0],
                "image_path": slide[1],
                "name": slide[2],
                "organ": slide[3],  
                "description": slide[4]
            }
            for slide in slide_locations
        ]

        return slide_info
    def clear_the_db(self):
        self.execute('''DELETE FROM slides''', commit=True)

    def clear_showen(self):
        self.execute('''DELETE FROM shown_slides''', commit=True)

    def get_all_slides_inf(self):
        slides_info = self.execute('''SELECT * FROM slides''', fetch=True)
        return slides_info
    def remove_shown_table(self):
        self.execute('''DROP TABLE IF EXISTS shown_slides''', commit=True)
        self.execute('''
            CREATE TABLE shown_slides (
                slide_id INTEGER,
                user_id INTEGER,
                shown_date TIMESTAMP,
                FOREIGN KEY (slide_id) REFERENCES slides (id)
            )''', commit=True)
    def update_record(self,slide_id,col_name,new_value):
        self.execute(f'''UPDATE slides SET {col_name} = ? WHERE  id = ?''', (new_value,slide_id), commit=True)


# slide.add_slide(2,"Gumboro,IBD","cloaca,cloacal bursa,bursa","E:\programming\Telegram bot project\slides_images\\gumboro_coloaca.png","""Swollen, 
# edematous, 
# and 
# hemorrhagic 
# cloacal bursa 
# from 
# an infected 
# chicken, 
# with IBD.""")
# slide.add_slide(3,"Gumboro,IBD","thigh,thigh muscle,thigh region, thigh region","E:\programming\Telegram bot project\slides_images\\gumboro_thigh.png","""Hemorrhage
#  in
#  muscle.
#  thigh
# """)
# slide.add_slide(4,"Avian influenza,influenza,AI","lung","E:\programming\Telegram bot project\slides_images\\AI_lung.png",""" Hemorrhage in the tip of glands 
# •focal area of inflammatory cell 
# infiltration between glands necrosis and 
# degeneration of glands with severe 
# inflammatory cell infiltration
# """)
# slide.add_slide(5,"Coccidea","bile, bile duct","E:\programming\Telegram bot project\slides_images\\coccidea_bile.png",""" 1- Presence of the developmental stages of coccida in 
# epithelial cells lining bile duct.
#  2- Hyperplasia and proliferation in epithelial lining bile 
# duct (Finger like projection inside  lumen of bile duct).
#  3-Eosinophilic cells infiltration.
#  4-Fibrosis around bile duct.
# """)
# slide.add_slide(6,"Infectious bovine rhinotracheitis,IBR","trachea","E:\programming\Telegram bot project\slides_images\\IBR_trachea.png",""" Tracheal mucosa is congested and covered by 
# mucopurulent exudate.
# """)
# slide.add_slide(7,"Malignant catarrhal fever,MCF","lymph node,lymph,node,ln","E:\programming\Telegram bot project\slides_images\\MCF_lymph.png","""  Swollen, enlarged and sever congested lymph nodes and on 
# cut section appeared granular and dull
# """)
# slide.add_slide(8,"Bovine leukosis,Bl","liver","E:\programming\Telegram bot project\slides_images\\bovinele_liver.png",""" The tumor cells consists of focal or diffuse sheets of 
# the neoplastic lymphocytes in interstitial tissue and 
# around congested blood vessels. 
# Liver: Between hepatocytes, portal triad and 
# around central vein. 
# """)
# slide.add_slide(9,"rabies","spinal cord, gray matter of spinal cord","E:\programming\Telegram bot project\slides_images\\rabies_spinal.png","""Hemorrhage
# in gray matter 
# of spinal cord
# """)
# slide.add_slide(10,"coccidea","liver","E:\programming\Telegram bot project\slides_images\\coccidea_liver_rabit.png","""Hepatic coccidiosis 
# byEimeria stiedaein a 
# rabbit. The liver is 
# exceptionally 
# hypertrophied 
# (enlarged) with small 
# pale nodules 
# corresponding to 
# lesions in the biliary 
# canals.
# """)
