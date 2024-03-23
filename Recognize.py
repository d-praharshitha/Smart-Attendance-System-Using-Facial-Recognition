import datetime
import os
import time
import PySimpleGUI as sg
import cv2
import pandas as pd

def recognize_attendance():
    sg.theme('DarkPurple1')
    layout = [
        [sg.Image(filename='', key='image')],
        [sg.Text(f'Date : {datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")}', key='date', font=('Helvetica 18'))], 
        [sg.Text(f'Time : {datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")}', key='time', font=('Helvetica 18'))],
        [sg.Button("Clock IN", size=(25,2), font=('Helvetica 13'), button_color=('white', '#303030')),
         sg.Button("Clock OUT", size=(25,2), font=('Helvetica 13'), button_color=('white', '#303030')),
         sg.Button("Save Attendance", size=(25,2), font=('Helvetica 13'), button_color=('white', 'green')),
         sg.Button("Back", size=(15,2), font=('Helvetica 13'), button_color=('white', 'red'))]
    ]
    screen_width, screen_height = sg.Window.get_screen_size()  # Get the screen size
    window = sg.Window('Mark Attendance', layout, auto_size_buttons=False, element_justification='c', finalize=True, location=(0, 0))
    window.set_min_size((screen_width, screen_height))  # Set the window size to max screen size

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("TrainingImageLabel"+os.sep+"Trainner.yml")
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    df = pd.read_csv("StudentDetails"+os.sep+"StudentDetails.csv")
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Clock IN Time', 'Clock OUT Time', 'Duration', 'Status']
    attendance = pd.DataFrame(columns=col_names)

    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 840)  # set video width
    cam.set(4, 680)  # set video height

    # Define min window size to be recognized as a face
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    lecture = sg.popup_get_text('Please Enter Lecture Duration', 'HH:MM:SS')

    while True:
        event, values = window.read(timeout=1)
        window.find_element('time').update(f'Date : {datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")}')
        window.find_element('time').update(f'Time : {datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")}')
        if event == 'Back':
            c = sg.PopupYesNo('Save Attendance ?')
            if c == 'No':
                cam.release()
                cv2.destroyAllWindows()
                window.close()
            elif c == 'Yes':
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                Hour, Minute, Second = timeStamp.split(":")
                fileName = "Attendance"+os.sep+"Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
                attendance.to_csv(fileName, index=False)
                cam.release()
                cv2.destroyAllWindows()
                window.close()
                sg.popup_timed('Attendance Successful')
            break
        elif event == "Save Attendance" or event == sg.WIN_CLOSED:
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            Hour, Minute, Second = timeStamp.split(":")

            attendance_file = "Attendance" + os.sep + f"Attendance_{date}.csv"
            fileName = attendance_file

            # If the file already exists, load existing data
            if os.path.exists(fileName):
                existing_attendance = pd.read_csv(fileName)
            else:
                existing_attendance = pd.DataFrame(columns=col_names)

            # Concatenate existing data with new attendance
            combined_attendance = pd.concat([existing_attendance, attendance], ignore_index=True)

            # Save the combined attendance to the same file
            combined_attendance.to_csv(fileName, index=False)
            sg.popup_timed('Attendance Successful')

            attendance = pd.DataFrame(columns=col_names)
            attendance.to_csv("Attendance.csv",index=False)

            cam.release()
            cv2.destroyAllWindows()
            window.close()
            break
        elif event == 'Clock IN':
            check = sg.PopupYesNo(f'{aa[0]} are you clocking In?')
            if check == 'Yes':
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa = str(aa)[2:-2]
                attendance.loc[len(attendance)] = [Id, aa, date, timeStamp, '-', '-', '-']
            elif check == 'N0':
                print('Not clocked IN')
        elif event == 'Clock OUT':
            check = sg.PopupYesNo(f'{aa[0]} are you clocking OUT?')
            if check == 'Yes':
                ts = time.time()
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                attendance.at[attendance[attendance['Id'] == Id].index.values, 'Clock OUT Time'] = timeStamp
        
                # Retrieve clock in and clock out times directly from DataFrame
                co = attendance.loc[attendance['Id'] == Id, 'Clock OUT Time'].values[0]
                ci = attendance.loc[attendance['Id'] == Id, 'Clock IN Time'].values[0]
        
                FMT = '%H:%M:%S'
                duration = datetime.datetime.strptime(co, FMT) - datetime.datetime.strptime(ci, FMT)
                attendance.at[attendance[attendance['Id'] == Id].index.values, 'Duration'] = duration
        
                d = datetime.datetime.strptime(lecture, FMT) - duration
                if int(str(d).split(':')[1]) in range(-5, 6):
                    attendance.at[attendance[attendance['Id'] == Id].index.values, 'Status'] = 'Present'
                else:
                    attendance.at[attendance[attendance['Id'] == Id].index.values, 'Status'] = 'MCR'
            elif check == 'No':
                print('Not clocked OUT')

        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5, minSize=(int(minW), int(minH)), flags=cv2.CASCADE_SCALE_IMAGE)
        for(x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x+w, y+h), (10, 159, 255), 2)
            Id, conf = recognizer.predict(gray[y:y+h, x:x+w])

            if conf < 100:
                aa = df.loc[df['Id'] == Id]['Name'].values
                confstr = "  {0}%".format(round(100 - conf))
                tt = str(Id)+"-"+aa
            else:
                Id = '  Unknown  '
                tt = str(Id)
                confstr = "  {0}%".format(round(100 - conf))
            tt = str(tt)[2:-2]
            if(100-conf) > 67:
                tt = tt + " [Pass]"
                cv2.putText(im, str(tt), (x+5,y-5), font, 1, (255, 255, 255), 2)
            else:
                cv2.putText(im, str(tt), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            if (100-conf) > 67:
                cv2.putText(im, str(confstr), (x + 5, y + h - 5), font,1, (0, 255, 0),1 )
            elif (100-conf) > 50:
                cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 255, 255), 1)
            else:
                cv2.putText(im, str(confstr), (x + 5, y + h - 5), font, 1, (0, 0, 255), 1)
        attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
        imgbytes = cv2.imencode(".png", im)[1].tobytes()
        window["image"].update(data=imgbytes)

    cam.release()
    cv2.destroyAllWindows()
    os.system('cls')
