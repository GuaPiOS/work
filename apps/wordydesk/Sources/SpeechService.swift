import AppKit
import AVFoundation
import Foundation

@MainActor
final class SpeechService {
    private let synthesizer = AVSpeechSynthesizer()
    private let phonemeSynthesizer = NSSpeechSynthesizer()
    private var audioPlayer: AVAudioPlayer?

    func speakWord(_ text: String, preferences: AppPreferences) async {
        await speak(text, kind: .word, preferences: preferences)
    }

    func speakSentence(_ text: String, preferences: AppPreferences) async {
        await speak(text, kind: .sentence, preferences: preferences)
    }

    private func bestAmericanVoice() -> AVSpeechSynthesisVoice? {
        let voices = AVSpeechSynthesisVoice.speechVoices()
        return voices.first(where: { $0.language == "en-US" && $0.quality == .enhanced })
            ?? voices.first(where: { $0.language == "en-US" })
            ?? AVSpeechSynthesisVoice(language: "en-US")
    }

    func phonemes(for text: String) -> String {
        let rawPhonemes = phonemeSynthesizer.phonemes(from: text)

        let cleaned = rawPhonemes
            .replacingOccurrences(of: "[[inpt TUNE]]", with: "")
            .replacingOccurrences(of: "%", with: " ")
            .replacingOccurrences(of: "_", with: " ")
            .trimmingCharacters(in: .whitespacesAndNewlines)

        return cleaned.isEmpty ? WordEntry.emptyPronunciation : cleaned
    }

    private func speak(_ text: String, kind: SpeechKind, preferences: AppPreferences) async {
        let normalized = kind == .sentence ? normalizeSentence(text) : text

        if let data = try? await remoteAudio(for: normalized, kind: kind, provider: preferences.speechProvider) {
            playAudioData(data)
            return
        }

        synthesizer.stopSpeaking(at: .immediate)
        let utterance = kind == .sentence
            ? makeUtterance(for: normalized, rate: 0.45, pitch: 1.01, delay: 0.18)
            : makeUtterance(for: normalized, rate: 0.41, pitch: 0.98, delay: 0.10)
        synthesizer.speak(utterance)
    }

    private func remoteAudio(for text: String, kind: SpeechKind, provider: SpeechProvider) async throws -> Data? {
        switch provider {
        case .system:
            return nil
        case .elevenLabs:
            return try await elevenLabsAudio(for: text)
        case .openAI:
            return try await openAIAudio(for: text, kind: kind)
        }
    }

    private func elevenLabsAudio(for text: String) async throws -> Data? {
        guard let preferences = currentPreferences,
              !preferences.elevenLabsAPIKey.isEmpty else {
            return nil
        }

        let apiKey = preferences.elevenLabsAPIKey
        let voiceID = preferences.elevenLabsVoiceID
        let url = URL(string: "https://api.elevenlabs.io/v1/text-to-speech/\(voiceID)")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue(apiKey, forHTTPHeaderField: "xi-api-key")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("audio/mpeg", forHTTPHeaderField: "Accept")

        let body: [String: Any] = [
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": [
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": true
            ]
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (data, response) = try await URLSession.shared.data(for: request)
        let statusCode = (response as? HTTPURLResponse)?.statusCode ?? 500
        return (200..<300).contains(statusCode) ? data : nil
    }

    private func openAIAudio(for text: String, kind: SpeechKind) async throws -> Data? {
        guard let preferences = currentPreferences,
              !preferences.openAIAPIKey.isEmpty else {
            return nil
        }

        let apiKey = preferences.openAIAPIKey
        let url = URL(string: "https://api.openai.com/v1/audio/speech")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = [
            "model": "gpt-4o-mini-tts",
            "voice": kind == .sentence ? "marin" : "cedar",
            "input": text,
            "format": "mp3",
            "instructions": kind == .sentence
                ? "Speak in a warm, natural American tone with gentle pacing and clear phrasing."
                : "Speak in a crisp natural American accent, like a thoughtful language tutor."
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (data, response) = try await URLSession.shared.data(for: request)
        let statusCode = (response as? HTTPURLResponse)?.statusCode ?? 500
        return (200..<300).contains(statusCode) ? data : nil
    }

    private func playAudioData(_ data: Data) {
        synthesizer.stopSpeaking(at: .immediate)
        audioPlayer = try? AVAudioPlayer(data: data)
        audioPlayer?.prepareToPlay()
        audioPlayer?.play()
    }

    private func makeUtterance(for text: String, rate: Float, pitch: Float, delay: TimeInterval) -> AVSpeechUtterance {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = bestAmericanVoice()
        utterance.rate = rate
        utterance.pitchMultiplier = pitch
        utterance.preUtteranceDelay = 0.03
        utterance.postUtteranceDelay = delay
        return utterance
    }

    private func normalizeSentence(_ text: String) -> String {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return text }
        return trimmed.hasSuffix(".") || trimmed.hasSuffix("!") || trimmed.hasSuffix("?")
            ? trimmed
            : trimmed + "."
    }

    private enum SpeechKind {
        case word
        case sentence
    }

    private var currentPreferences: AppPreferences?

    func bind(preferences: AppPreferences) {
        currentPreferences = preferences
    }
}
