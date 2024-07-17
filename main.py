#size needs to be set before any import
from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '800')



from kivy.app import App
from kivy.uix.label import Label 
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget 
from kivy.uix.tabbedpanel import TabbedPanel 
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, Rectangle, Line
import json
from kivy.clock import Clock
from functools import partial
import os
from kivy.core.audio import SoundLoader


class CustomLabel(Label):
    def __init__(self, **kwargs):
        super(CustomLabel, self).__init__(**kwargs)

        # Add default properties here
        self.border_color = (53/255, 56/255, 54/255, 1)  # RGBA format (red)
        self.border_width = 3

    def on_size(self, *args):
        self.update_canvas()

    def on_pos(self, *args):
        self.update_canvas()

    def update_canvas(self):
        self.canvas.before.clear()
        with self.canvas.before:
            # Draw background color
            Color(92/255, 94/255, 92/255, 1)  # RGBA format (green)
            Rectangle(pos=self.pos, size=self.size)

            # Draw border
            Color(*self.border_color)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=self.border_width)



class MyLayout(TabbedPanel): 

    def __init__(self,**kwargs):
        super(MyLayout, self).__init__(**kwargs)
        self.load_saved_classrooms()

        #load sound
        self.sound = SoundLoader.load('sound/rollcall_sound.wav')
        self.sound2= SoundLoader.load('sound/popup_sound.mp3')

        #creating ToggleButton of Register
        self.create_buttons()

        with open("test_call.txt","w") as f:
            for i in range(1,101):
                f.write(f"{i} {0}\n")
        
        with open("test_classroom.txt","w") as f:
            f.write("EMPTY")

    def exit_app(self):
        App.get_running_app().stop()


    def load_saved_classrooms(self):
        try:
            with open('classrooms.json','r') as f:
                classrooms = json.load(f)
                for cn in classrooms:
                    cat = ToggleButton(text=cn, font_size=24, group="A")
                    cat.bind(on_press=self.func)
                    self.ids.roll_call.add_widget(cat)
        except:
            pass

    
    def create_buttons(self):
        for i in range(1,101):
            btn = ToggleButton(text=str(i),font_size=32,size_hint_x=None, size_hint_y=None,height=100, width=104)
            btn.bind(on_press =partial(self.on_toggle_button,roll=i))
            self.ids.kaka.add_widget(btn)
    


    def on_toggle_button(self, instance, roll, *args):
        value = 1 if instance.state == 'down' else 0 
        #add sound if click on roll number
        if self.sound:
            self.sound.play()
        #roll present/absent
        with open("test_call.txt","a") as f:
            f.write(f"{roll} {value}\n")

    
    def reset_toggle_buttons(self):
        for child in self.ids.roll_call.children:
            if isinstance(child, ToggleButton):
                child.state = 'normal'
        for child in self.ids.kaka.children:
            if isinstance(child, ToggleButton):
                child.state = 'normal'


    def no_class_select_popup(self):
        content = BoxLayout(orientation='vertical',padding=10,spacing=10)
        lb = Label(text="No ClassRoom Selected", font_size=20)
        content.add_widget(lb)
        popup = Popup(title='Error Notice', content=content, size_hint=(0.8,0.3))
        popup.open()

    def play_sound(self):
        if self.sound:
            self.sound.play()

    
        
        
            

    def final_submit(self):
        roll_state_data = {}
        with open("test_call.txt","r") as f:
            for line in f:
                parts = line.strip().split()
                roll = parts[0]
                state = parts[1]
                roll_state_data[roll]=int(state)

        previous_data = {}
        with open("test_classroom.txt","r") as f:
            file_name = f.read()

        #if no classroom selected
        if file_name=='EMPTY':
            if self.sound2:
                self.sound2.play()
            self.no_class_select_popup()
            return 


        file_name=file_name+".txt"

        with open(file_name,"r") as f:
            for line in f:
                parts = line.strip().split()
                roll = parts[0]
                state = parts[1]
                previous_data[roll]=int(state)

        combined_data = {}
        for roll in roll_state_data:
            if roll in previous_data:
                t = roll_state_data[roll]+previous_data[roll]
                combined_data[roll]=t 
        
        with open(file_name,"w") as f:
            for i,j in combined_data.items():
                f.write(f"{i} {j}\n")

        #show on Details Page the info
        self.classDetails(file_name)

        #reset the temp files and toggle btn
        with open("test_call.txt","w") as f:
            for i in range(1,101):
                f.write(f"{i} {0}\n")
        
        with open("test_classroom.txt","w") as f:
            f.write("EMPTY")
        self.reset_toggle_buttons()



    def add_classroom(self):
        #creating popup content
        content = BoxLayout(orientation='vertical',padding=10,spacing=10)
        input_name = TextInput(hint_text="Enter ClassRoom Name to Add", multiline=False,size_hint=(1,0.3), font_size=20, halign='center')

        content.add_widget(input_name)

        def on_submit(instance):
            if self.sound:
                self.sound.play()
            cn = input_name.text 
            if cn:
                #this line creates button(classroom) dynamically on id roll_call
                cat = ToggleButton(text=cn, font_size=24, group="A")
                cat.bind(on_press=self.func)
                self.ids.roll_call.add_widget(cat)


                #add to json
                try:
                    with open('classrooms.json','r') as f:
                        classrooms = json.load(f)
                except:
                    classrooms=[]

                if cn not in classrooms:
                    classrooms.append(cn)

                with open("classrooms.json","w") as f:
                    json.dump(classrooms, f)

                #Adding student database for classroom(cn)

                filename = cn+".txt"
                with open(filename,"w") as f:
                    for i in range(1,101):
                        f.write(f"{i} 0\n")
                

            popup.dismiss()

        #creating submit button
        sb = Button(text="Submit", size_hint=(1, 0.3))
        sb.bind(on_press=on_submit)
        content.add_widget(sb)

        #creating the popup
        popup = Popup(title='Add New ClassRoom', content=content, size_hint=(0.8,0.3))
        popup.open()



    def func(self,instance):
        #add sound
        if self.sound:
            self.sound.play()

        #instance.text is the button name(class name)
        with open("test_classroom.txt","w") as f:
            f.write(f"{instance.text}")

        #when pressed details page also updates 
        fn = instance.text+".txt"
        self.classDetails(fn)


    def delete_class(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        input_name = TextInput(hint_text="Enter ClassRoom Name to Delete", size_hint=(1,0.3),font_size=20, multiline=False)
        content.add_widget(input_name)

        def on_delete(instance):
            if self.sound:
                self.sound.play()

            class_name = input_name.text.strip()
            for child in self.ids.roll_call.children[:]:
                if isinstance(child, ToggleButton) and child.text == class_name:


                    #Removing classroom details
                    classroom_name = class_name
                    try:
                        # Load the JSON data from the file
                        with open("classrooms.json", 'r') as file:
                            classrooms = json.load(file)
                        # Check if the classroom exists in the list and remove it
                        if classroom_name in classrooms:
                            classrooms.remove(classroom_name)
                        with open("classrooms.json", 'w') as file:
                            json.dump(classrooms, file, indent=4)

                    except:
                        pass 

                    fn = class_name+".txt"
                    os.remove(fn)

                    self.ids.roll_call.remove_widget(child)
                    break

            popup.dismiss()

        db = Button(text="Delete", size_hint=(1, 0.3))
        db.bind(on_press=on_delete)
        content.add_widget(db)

        popup = Popup(title='Delete ClassRoom', content=content, size_hint=(0.8, 0.3))
        popup.open()




    def classDetails(self,filename):
        #clear previous data/widgets
        self.ids.det.clear_widgets()

        file_name = filename.split('.')[0]

        lab = CustomLabel(text="ClassRoom: "+file_name,font_size=32,bold=True,color=(1, 1, 1, 1))
        self.ids.det.add_widget(lab)

        lab = CustomLabel(text="***************",font_size=32,bold=True,color=(1, 1, 1, 1))
        self.ids.det.add_widget(lab)

        with open(filename,"r") as f:
            for line in f:
                parts = line.strip().split()
                roll = parts[0]
                state = parts[1]

                pa = "Roll No: "+roll+"    "+"Present Day: "+state

                lab = CustomLabel(text=pa,font_size=32,bold=False,color=(1, 1, 1, 1))
                self.ids.det.add_widget(lab)

    def cancel_btn(self):
        #reset the temp files and toggle button
        with open("test_call.txt","w") as f:
            for i in range(1,101):
                f.write(f"{i} {0}\n")
        
        with open("test_classroom.txt","w") as f:
            f.write("EMPTY")
        self.reset_toggle_buttons()



        
class AttendenceApp(App):
    def build(self):
        return MyLayout()



if __name__=="__main__":
    AttendenceApp().run()
