#include <iostream>
#include <Windows.h>
#include <vector>
#include <cmath>

constexpr int CHUNK_SIZE = 1024;
constexpr int SAMPLING_RATE = 2000;
constexpr int BITS_PER_SAMPLE = 16;

bool InitializeAudioInput(HWAVEIN& hWaveIn, WAVEFORMATEX& waveFormat, WAVEHDR& waveHeader)
{
    waveFormat.wFormatTag = WAVE_FORMAT_PCM;
    waveFormat.nChannels = 1;
    waveFormat.nSamplesPerSec = SAMPLING_RATE;
    waveFormat.nAvgBytesPerSec = SAMPLING_RATE * BITS_PER_SAMPLE / 8;
    waveFormat.nBlockAlign = BITS_PER_SAMPLE / 8;
    waveFormat.wBitsPerSample = BITS_PER_SAMPLE;
    waveFormat.cbSize = 0;

    MMRESULT result = waveInOpen(&hWaveIn, WAVE_MAPPER, &waveFormat, 0, 0, WAVE_FORMAT_DIRECT);
    if (result != MMSYSERR_NOERROR)
    {
        std::cerr << "Failed to open audio input device." << std::endl;
        return false;
    }

    waveHeader.lpData = reinterpret_cast<LPSTR>(new short[CHUNK_SIZE]);
    waveHeader.dwBufferLength = CHUNK_SIZE * sizeof(short);
    waveHeader.dwBytesRecorded = 0;
    waveHeader.dwUser = 0;
    waveHeader.dwFlags = 0;
    waveHeader.dwLoops = 0;
    waveInPrepareHeader(hWaveIn, &waveHeader, sizeof(WAVEHDR));

    return true;
}

void CleanupAudioInput(HWAVEIN& hWaveIn, WAVEHDR& waveHeader)
{
    waveInUnprepareHeader(hWaveIn, &waveHeader, sizeof(WAVEHDR));
    waveInClose(hWaveIn);
    delete[] waveHeader.lpData;
}

void DrawChart(const std::vector<double>& data)
{
    system("cls");

    for (double value : data)
    {
        int numStars = static_cast<int>(value / 1000);
        for (int i = 0; i < numStars; ++i)
        {
            std::cout << "*";
        }
        std::cout << std::endl;
    }
}

int main()
{
    HWAVEIN hWaveIn;
    WAVEFORMATEX waveFormat;
    WAVEHDR waveHeader;
    if (!InitializeAudioInput(hWaveIn, waveFormat, waveHeader))
    {
        return 1;
    }

    waveInStart(hWaveIn);

    std::vector<double> chartData(CHUNK_SIZE);
    while (true)
    {
        waveInAddBuffer(hWaveIn, &waveHeader, sizeof(WAVEHDR));
        waveInStart(hWaveIn);
        waveInStop(hWaveIn);
        for (int i = 0; i < CHUNK_SIZE; ++i)
        {
            chartData[i] = std::abs(static_cast<double>(reinterpret_cast<short*>(waveHeader.lpData)[i]));
        }

        DrawChart(chartData);
    }

    CleanupAudioInput(hWaveIn, waveHeader);

    return 0;
}
