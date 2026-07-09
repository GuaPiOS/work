import Foundation

enum SpeechProvider: String, CaseIterable, Identifiable {
    case system
    case elevenLabs
    case openAI

    var id: String { rawValue }

    var title: String {
        switch self {
        case .system:
            return "System"
        case .elevenLabs:
            return "ElevenLabs"
        case .openAI:
            return "OpenAI"
        }
    }

    var subtitle: String {
        switch self {
        case .system:
            return "Offline, instant"
        case .elevenLabs:
            return "Most natural with ELEVENLABS_API_KEY"
        case .openAI:
            return "Natural with OPENAI_API_KEY"
        }
    }
}
