import os
import Capture_Image
import Train_Image
import Recognize
import view_attendance
import PySimpleGUI as sg
import cv2

def mainMenu():
    menu_def = [['&File', ['&Open Attendance Folder', '&Open Student Records','---', '&Exit', ]]]
    sg.theme('DarkPurple1')

    # Load the video file
    video_path = 'Images/Face_Recognition.mp4'
    cap = cv2.VideoCapture(video_path)

    # Get the maximum available screen size
    screen_width, screen_height = sg.Window.get_screen_size()

    layout = [
        [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
        [sg.Text('Attendance Capture System Using Face Recognition ', font='Helvetica 30', justification='center')],
        [sg.Column([[sg.Image(filename='', size=(screen_width, screen_height), key='-VIDEO-')]], justification='center')],  # Set the image size to the maximum available screen size
        [sg.Column([
            [sg.Button("Mark Attendance", size=(82, 2), font='Helvetica 14', button_color=('white', 'green'))],
            [sg.Button("Add Person", size=(40, 2), font='Helvetica 14', button_color=('white', '#303030'), key='-ADDPERSON-'), sg.Button("Train Images", size=(40, 2), font='Helvetica 14', button_color=('white', '#303030'), key='-TRAINIMAGES-')],
            [sg.Button("View Attendance", size=(40, 2), font='Helvetica 14', button_color=('white', '#303030')), sg.Button("Quit", size=(40, 2), font='Helvetica 14', button_color=('white', 'red'))]
        ], justification='center')]
    ]

    # Create the PySimpleGUI window
    window = sg.Window('Face Attendance Recognition Program', layout, finalize=True)

    # Hide the title bar and borders
    window.TKroot.attributes('-fullscreen', True)
    window.TKroot.attributes('-topmost', True)

    while True:
        event, values = window.read(timeout=20)  # Timeout set to 20ms for smoother video playback
        if event == sg.WINDOW_CLOSED or event == 'Quit' or event == 'Exit':
            break
        elif event == "Open Attendance Folder":
            path = "Attendance"
            path = os.path.realpath(path)
            os.startfile(path)
        elif event == "Open Student Records":
            path = "StudentDetails"
            path = os.path.realpath(path)
            os.startfile(path)
        elif event == "-ADDPERSON-":
            window.close()
            Capture_Image.takeImages()
            mainMenu()
            break
        elif event == "-TRAINIMAGES-":
            window.close()
            Train_Image.TrainImages()
            mainMenu()
            break
        elif event == "Mark Attendance":
            window.close()
            Recognize.recognize_attendance()
            mainMenu()
            break
        elif event == "View Attendance":
            window.close()
            view_attendance.vcsv()
            mainMenu()
            break

        # Read a frame from the video and convert it to a format suitable for PySimpleGUI
        ret, frame = cap.read()
        if ret:
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window['-VIDEO-'].update(data=imgbytes)
        else:
            # If the video reaches its end, reset to the beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    window.close()

if __name__ == "__main__":
    mainMenu()
