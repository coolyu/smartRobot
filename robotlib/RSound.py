# -*- coding: utf-8 -*-
import os
import pygame
import pyaudio
import wave
import logging
from sys import byteorder
from array import array
from struct import pack



class RSound:
    def __init__(self):
        self.THRESHOLD = 12000
        self.CHUNK_SIZE = 1024
        self.FORMAT = pyaudio.paInt16
        self.RATE = 16000
        self.MAX_WAITTIME = 10
        self.MAX_SILENTWAIT = 200
        pygame.mixer.init(frequency=16000, size=-16, channels=1, buffer=1024)
        self.log = logging.getLogger('RSound')

    def playsound(self,soundfile):
        if os.path.isfile(soundfile):
            pygame.mixer.music.load(soundfile)
            pygame.mixer.music.play(0)
            clock = pygame.time.Clock()
            clock.tick(100)
            while pygame.mixer.music.get_busy():
                clock.tick(100)

    def is_silent(self,snd_data):
        "Returns 'True' if below the 'silent' threshold"
        return max(snd_data) < self.THRESHOLD

    def normalize(self,snd_data):
        "Average the volume out"
        MAXIMUM = 16384
        times = float(MAXIMUM)/max(abs(i) for i in snd_data)
        r = array('h')
        for i in snd_data:
            r.append(int(i*times))
        return r

    def trim(self ,snd_data):
        "Trim the blank spots at the start and end"
        def _trim(snd_data):
            snd_started = False
            r = array('h')

            for i in snd_data:
                if not snd_started and abs(i)>self.THRESHOLD:
                    snd_started = True
                    r.append(i)

                elif snd_started:
                    r.append(i)
            return r

        # Trim to the left
        snd_data = _trim(snd_data)

        # Trim to the right
        snd_data.reverse()
        snd_data = _trim(snd_data)
        snd_data.reverse()
        return snd_data

    def add_silence(self , snd_data, seconds):
        "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
        r = array('h', [0 for i in xrange(int(seconds*self.RATE))])
        r.extend(snd_data)
        r.extend([0 for i in xrange(int(seconds*self.RATE))])
        return r

    def record(self):
        """
        Record a word or words from the microphone and
        return the data as an array of signed shorts.

        Normalizes the audio, trims silence from the
        start and end, and pads with 0.5 seconds of
        blank sound to make sure VLC et al can play
        it without getting chopped off.
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=1, rate=self.RATE,
            input=True,frames_per_buffer=self.CHUNK_SIZE)

        num_silent = 0
        snd_started = False

        is_timeout = False

        r = array('h')
        timewaiting = 0
        while 1:
            # little endian, signed short


            snd_data = array('h', stream.read(self.CHUNK_SIZE))
            if byteorder == 'big':
                snd_data.byteswap()
            silent = self.is_silent(snd_data)

            if snd_started:
                r.extend(snd_data)
            else:
                if silent:
                    timewaiting += 1
                    if timewaiting > self.MAX_SILENTWAIT:
                        is_timeout = True
                        break


            if silent and snd_started:
                num_silent += 1
            elif not silent and not snd_started:
                snd_started = True

            if snd_started and num_silent > self.MAX_WAITTIME:
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

        if is_timeout == True:
            sample_width = -1
        else:
            self.log.debug("max sound is %d " % max(r))
            sample_width = p.get_sample_size(self.FORMAT)
            r = self.normalize(r)
            r = self.trim(r)
            r = self.add_silence(r, 0.5)




        return sample_width, r

    def record_to_file(self , path):
        "Records from the microphone and outputs the resulting data to 'path'"
        sample_width, data = self.record()
        if sample_width > -1:
            data = pack('<' + ('h'*len(data)), *data)

            wf = wave.open(path, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(sample_width)
            wf.setframerate(self.RATE)
            wf.writeframes(data)
            wf.close()
        else:
            vol = open(path,"wb")
            vol.close()