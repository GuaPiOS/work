import Foundation

@MainActor
final class AppPreferences: ObservableObject {
    @Published var autoSpeakEnabled: Bool {
        didSet { defaults.set(autoSpeakEnabled, forKey: Keys.autoSpeakEnabled) }
    }
    @Published var autoCaptureEnabled: Bool {
        didSet { defaults.set(autoCaptureEnabled, forKey: Keys.autoCaptureEnabled) }
    }
    @Published var speechProviderRawValue: String {
        didSet { defaults.set(speechProviderRawValue, forKey: Keys.speechProviderRawValue) }
    }
    @Published var dailyGoal: Int {
        didSet { defaults.set(dailyGoal, forKey: Keys.dailyGoal) }
    }
    @Published var reminderEnabled: Bool {
        didSet { defaults.set(reminderEnabled, forKey: Keys.reminderEnabled) }
    }
    @Published var onboardingCompleted: Bool {
        didSet { defaults.set(onboardingCompleted, forKey: Keys.onboardingCompleted) }
    }
    @Published var openAIAPIKey: String {
        didSet { defaults.set(openAIAPIKey, forKey: Keys.openAIAPIKey) }
    }
    @Published var elevenLabsAPIKey: String {
        didSet { defaults.set(elevenLabsAPIKey, forKey: Keys.elevenLabsAPIKey) }
    }
    @Published var elevenLabsVoiceID: String {
        didSet { defaults.set(elevenLabsVoiceID, forKey: Keys.elevenLabsVoiceID) }
    }

    var speechProvider: SpeechProvider {
        get { SpeechProvider(rawValue: speechProviderRawValue) ?? .system }
        set { speechProviderRawValue = newValue.rawValue }
    }

    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        self.autoSpeakEnabled = defaults.object(forKey: Keys.autoSpeakEnabled) as? Bool ?? true
        self.autoCaptureEnabled = defaults.object(forKey: Keys.autoCaptureEnabled) as? Bool ?? true
        self.speechProviderRawValue = defaults.string(forKey: Keys.speechProviderRawValue) ?? SpeechProvider.system.rawValue
        let storedGoal = defaults.integer(forKey: Keys.dailyGoal)
        self.dailyGoal = storedGoal > 0 ? storedGoal : 8
        self.reminderEnabled = defaults.object(forKey: Keys.reminderEnabled) as? Bool ?? false
        self.onboardingCompleted = defaults.object(forKey: Keys.onboardingCompleted) as? Bool ?? false
        self.openAIAPIKey = defaults.string(forKey: Keys.openAIAPIKey) ?? ""
        self.elevenLabsAPIKey = defaults.string(forKey: Keys.elevenLabsAPIKey) ?? ""
        self.elevenLabsVoiceID = defaults.string(forKey: Keys.elevenLabsVoiceID) ?? "EXAVITQu4vr4xnSDxMaL"
    }

    private enum Keys {
        static let autoSpeakEnabled = "wordydesk.autoSpeakEnabled"
        static let autoCaptureEnabled = "wordydesk.autoCaptureEnabled"
        static let speechProviderRawValue = "wordydesk.speechProviderRawValue"
        static let dailyGoal = "wordydesk.dailyGoal"
        static let reminderEnabled = "wordydesk.reminderEnabled"
        static let onboardingCompleted = "wordydesk.onboardingCompleted"
        static let openAIAPIKey = "wordydesk.openAIAPIKey"
        static let elevenLabsAPIKey = "wordydesk.elevenLabsAPIKey"
        static let elevenLabsVoiceID = "wordydesk.elevenLabsVoiceID"
    }
}
