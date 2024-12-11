import customtkinter as ctk
from customtkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from spleeter.separator import Separator
import os
from pydub import AudioSegment #importar pyaudio para funcionar
from pydub.playback import play, _play_with_simpleaudio
import threading
import multiprocessing
from datetime import datetime
from preprocess import preprocess
from player import player
#from visualizacao import bolas



faixas = [0,0,0,0,0]
faixasStr = ["vocals.wav","bass.wav","drums.wav","piano.wav","other.wav"]
caminho = "All Guns Blazing.mp3"
tempoMusica = 0
#thread_musica = None
tempoInicioMusica = None
play_obj = None
paused = False

'''
def reproduzMusica(path, tempo, volume):
    global play_obj, tempoMusica
    musica = AudioSegment.from_mp3(path)
    musica = musica - volume
    #print(tempo)
    play_obj = _play_with_simpleaudio(musica[(tempo*1000):])
    #play(musica[(tempo * 1000):])
'''
def exportaMp3(musica):
    musica.export("Musica_separada.mp3", format="mp3")

def reproduzMusica():
    global caminho, tempoMusica, paused, play_obj, tempoInicioMusica, faixas
    '''
    thread_musica = threading.Thread(target=reproduzMusica, args=(caminho,tempoMusica,volume,), daemon=True)
    thread_musica.start()
    '''
    nomeAudio = caminho.split("/")[-1].split(".")[0]

    musica = juntaAudio(faixas, nomeAudio)
    if not musica:
        lblWarning.configure(text="Selecione uma faixa")
    else:
        lblWarning.configure(text="")
        volume = abs((sldSpeaker.get()/2)-50)
        musica = musica - volume

        thread_export = threading.Thread(target=exportaMp3, args=(musica,), daemon=True)
        thread_export.start()
        #musica.export("Musica_separada.mp3", format="mp3")

        #print("teste\n")
        #play_obj = _play_with_simpleaudio(musica[(tempoMusica*1000):])
        #play_obj = multiprocessing.Process(target=player)
        player()


        paused = False
        tempoInicioMusica = datetime.now()

        btnPausa.configure(state="normal")
        btnReproduz.configure(state="disabled")

def juntaAudio(faixas, arq):
    global faixasStr
    audio = None
    for i in range (5):
        if faixas[i] and not audio:
            path = "output/" + arq + "/" + faixasStr[i]
            #print(path+"\n")
            audio = AudioSegment.from_wav(path)
        elif faixas[i]:
            path = "output/" + arq + "/" + faixasStr[i]
            #print(path+"\n")
            newAudio = AudioSegment.from_wav(path)
            audio = audio.overlay(newAudio)
    return audio

def reproduzir():
    tatil = sldTatil.get()
    speaker = sldSpeaker.get()
    global faixas
    faixas[0] = check1.get()
    faixas[1] = check2.get()
    faixas[2] = check3.get()
    faixas[3] = check4.get()
    faixas[4] = check5.get()

    #print(f"Tatil: {tatil}%\tSpeaker: {speaker}%\nVocal: {vocal}\nGuitarra: {guitarra}\nBateria: {bateria}\nPiano: {piano}")
    #threadBolas = threading.Thread(target=bolas, daemon=True)
    #threadBolas.start()
    reproduzMusica()
    

    #os.system("cd output")
    #os.system("ffmpeg -i vocal.wav -vn -ar 44100 -ac 2 -b:a 192k vocal.mp3")



def pausar():
    global play_obj, tempoMusica, tempoInicioMusica, paused
    paused = True
    play_obj.stop()

    deltaTempo = datetime.now() - tempoInicioMusica
    tempoMusica += deltaTempo.total_seconds()
    #print(tempoMusica)    

    btnPausa.configure(state="disabled")
    btnReproduz.configure(state="normal")

def check_playing(pausa):
    global play_obj, tempoMusica, paused

    if play_obj and not play_obj.is_playing() and not paused:
        btnPausa.configure(state="disabled")
        btnReproduz.configure(state="normal")
        #print("reset\n")
        tempoMusica = 0
        play_obj = None
    
    #pausa.after(500, lambda: check_playing(pausa))

def processaAudio(path):
    global caminho
    caminho = path
    separator = Separator('spleeter:5stems')
    separator.separate_to_file(path, 'output')
    nomeAudio = caminho.split("/")[-1].split(".")[0]
    bateria = AudioSegment.from_wav("output/"+nomeAudio+"/"+"vocals.wav") ############################################
    bateria.export("bateria.mp3",format="mp3")
    preprocess("bateria.mp3")
    btnReproduz.configure(state="normal")
    print("Separação concluída. Arquivos salvos na pasta 'output'.")

def carregaAudio():
    path = filedialog.askopenfilename(filetypes=[("Arquivos MP3", "*.mp3")])
    audio.configure(state="normal")
    audio.delete("1.0","500.0")
    if path.endswith(".mp3"):
        processaAudio(path)
        nomeAudio = path.split("/")[-1]
        audio.insert("1.0", f"Arquivo '{nomeAudio}' carregado com sucesso!")
    else:
        audio.insert("1.0",f"Arraste um arquivo .mp3")
    audio.configure(state="disabled")

def arrasta(drop):
    path = (drop.data).strip("{}")
    audio.configure(state="normal")
    audio.delete("1.0","500.0")
    if path.endswith(".mp3"):
        processaAudio(path)
        nomeAudio = path.split("/")[-1]
        audio.insert("1.0", f"Arquivo '{nomeAudio}' carregado com sucesso!")
    else:
        audio.insert("1.0",f"Arraste um arquivo .mp3")
    audio.configure(state="disabled")

def sliderSpk(value):
    lblVolSpeaker.configure(text=str(value)+"%")

def sliderTatil(value):
    lblVolTatil.configure(text=str(value)+"%")


if __name__ == '__main__':
    #Configuração da janela
    janela = TkinterDnD.Tk()
    janela.title("Music Configuration")
    janela.configure(background="#1a1a1a")
    janela.geometry("500x300")
    janela.resizable(False,False)


    #Componentes da janela
    audio = ctk.CTkTextbox(janela, activate_scrollbars=False)
    audio.place(relx=0.15, rely =0.05, relheight= 0.2)
    audio.insert("1.0","Arraste um audio")
    audio.configure(state="disabled")

    audio.drop_target_register(DND_FILES)
    audio.dnd_bind("<<Drop>>", arrasta)

    btnCarrega = ctk.CTkButton(janela,text="Carregar",command=carregaAudio)
    btnCarrega.place(relx = 0.6, rely =0.05)

    lblFaixa = ctk.CTkLabel(janela,text="Faixas")
    lblFaixa.place(relx=0.1, rely=0.25)

    check1 = ctk.CTkCheckBox(janela, text="Vocal")
    check1.place(relx=0.1, rely=0.35)

    check2 = ctk.CTkCheckBox(janela, text="Baixo")
    check2.place(relx=0.4, rely=0.35)

    check3 = ctk.CTkCheckBox(janela, text="Bateria")
    check3.place(relx=0.1, rely=0.45)

    check4 = ctk.CTkCheckBox(janela, text="Piano")
    check4.place(relx=0.4, rely=0.45)

    check5 = ctk.CTkCheckBox(janela, text="Outros")
    check5.place(relx=0.7, rely=0.35)

    lblTatil = ctk.CTkLabel(janela,text="Tatil")
    lblTatil.place(relx=0.1, rely=0.55)

    lblSpeaker = ctk.CTkLabel(janela,text="Speaker")
    lblSpeaker.place(relx=0.5, rely=0.55)

    sldTatil = ctk.CTkSlider(janela, from_=0, to=100, command=sliderTatil,number_of_steps=200)
    sldTatil.place(relx=0.1, rely=0.65)

    lblVolTatil = ctk.CTkLabel(janela, text="50%", height=8)
    lblVolTatil.place(relx=0.27, rely=0.71)

    lblVolSpeaker = ctk.CTkLabel(janela, text="50%", height=8)
    lblVolSpeaker.place(relx=0.67, rely=0.71)

    sldSpeaker = ctk.CTkSlider(janela, from_=0, to=100, command=sliderSpk,number_of_steps=200)
    sldSpeaker.place(relx=0.5, rely=0.65)

    lblWarning = ctk.CTkLabel(janela, text="", text_color="red")
    lblWarning.place(relx=0.375, rely=0.9)

    btnReproduz = ctk.CTkButton(janela,text="Reproduz", command=reproduzir)
    btnReproduz.place(relx=0.1, rely=0.8)

    btnPausa = ctk.CTkButton(janela,text="Pausar", command=pausar)
    btnPausa.place(relx=0.6, rely=0.8)

    #loop
    check_playing(btnPausa)
    janela.mainloop()
