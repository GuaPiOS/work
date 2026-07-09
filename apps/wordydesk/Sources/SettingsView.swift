import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var appModel: AppModel
    @EnvironmentObject private var preferences: AppPreferences

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("Preferences")
                .font(.title2.weight(.semibold))

            Toggle("Auto capture after selection", isOn: $preferences.autoCaptureEnabled)
            Toggle("Auto read after capture", isOn: $preferences.autoSpeakEnabled)
            Toggle("Daily reminder", isOn: $preferences.reminderEnabled)
                .onChange(of: preferences.reminderEnabled) { _, _ in
                    appModel.refreshReminderPreference()
                }

            Stepper(value: $preferences.dailyGoal, in: 3...30) {
                Text("Daily goal: \(preferences.dailyGoal)")
            }

            Picker("Voice", selection: $preferences.speechProviderRawValue) {
                ForEach(SpeechProvider.allCases) { provider in
                    Text(provider.title).tag(provider.rawValue)
                }
            }
            .tint(.black)

            if preferences.speechProvider == .openAI {
                SecureField("OpenAI API key", text: $preferences.openAIAPIKey)
                    .textFieldStyle(.roundedBorder)
            }

            if preferences.speechProvider == .elevenLabs {
                SecureField("ElevenLabs API key", text: $preferences.elevenLabsAPIKey)
                    .textFieldStyle(.roundedBorder)
                TextField("ElevenLabs voice id", text: $preferences.elevenLabsVoiceID)
                    .textFieldStyle(.roundedBorder)
            }

            Text("Cloud voice is optional. If the selected provider has no key, WordyDesk falls back to the system voice.")
                .font(.caption)
                .foregroundStyle(.secondary)

            Text(appModel.markdownFilePath().path)
                .font(.system(.body, design: .monospaced))
                .textSelection(.enabled)

            Spacer()
        }
        .padding(20)
        .background(Color.white)
        .preferredColorScheme(.light)
    }
}
