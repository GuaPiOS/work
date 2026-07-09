import AppKit
import AVFoundation
import Carbon
import Foundation

@MainActor
final class AppModel: ObservableObject {
    @Published var currentEntry: WordEntry?
    @Published var recentSavedEntries: [WordEntry] = []
    @Published var studyRecords: [StudyRecord] = []
    @Published var statusMessage = "Select a word and release the mouse to capture it."
    @Published var lastError: String?
    @Published var showingGuide = false

    let hotKeyHint = "Option-Command-G"
    let preferences = AppPreferences()

    private let selectionCapture = SelectionCaptureService()
    private let speechService = SpeechService()
    private let exampleGenerator = ExampleSentenceGenerator()
    private let dictionaryLookup = DictionaryLookupService()
    private let favoritesStore = FavoritesStore()
    private let studyStore = StudyStore()
    private let reminderScheduler = ReminderScheduler()
    private let quickPopupController = QuickPopupController()
    private var hotKeyManager: HotKeyManager?
    private var selectionMonitor: SelectionMonitor?
    private var lastCapturedWord = ""
    private var lastCaptureTime = Date.distantPast

    init() {
        speechService.bind(preferences: preferences)
        do {
            try WordyDeskPaths.migrateLegacyFilesIfNeeded()
        } catch {
            lastError = error.localizedDescription
        }
        loadSavedEntries()
        loadStudyRecords()
        reminderScheduler.update(enabled: preferences.reminderEnabled)
        hotKeyManager = HotKeyManager { [weak self] in
            Task { @MainActor in
                await self?.captureSelectedWord(trigger: .hotKey)
            }
        }
        hotKeyManager?.register()
        selectionMonitor = SelectionMonitor { [weak self] in
            Task { @MainActor in
                await self?.captureSelectedWord(trigger: .selection)
            }
        }
        selectionMonitor?.start()
    }

    func captureSelectedWord(trigger: CaptureTrigger = .manual) async {
        do {
            guard preferences.autoCaptureEnabled || trigger != .selection else { return }

            if trigger != .selection {
                statusMessage = "Capturing selected text..."
            }

            let text = try await selectionCapture.captureSelection()
            await handleIncomingText(text, trigger: trigger)
        } catch {
            guard trigger != .selection else { return }
            let message = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            lastError = message
            statusMessage = "Capture failed."
        }
    }

    func handleIncomingText(_ text: String, trigger: CaptureTrigger) async {
        let normalizedWord = WordNormalizer.normalize(text)
        guard !normalizedWord.isEmpty else {
            lastError = AppError.invalidSelection.errorDescription
            return
        }

        guard shouldAcceptCapture(word: normalizedWord, trigger: trigger) else {
            return
        }

        let sentence = exampleGenerator.makeSentence(for: normalizedWord)
        let definition = dictionaryLookup.definition(for: normalizedWord)
        let phonemes = speechService.phonemes(for: normalizedWord)
        let entry = WordEntry(
            word: normalizedWord,
            definition: definition,
            phonemes: phonemes,
            exampleSentence: sentence,
            createdAt: Date()
        )

        currentEntry = entry
        lastCapturedWord = normalizedWord
        lastCaptureTime = Date()
        statusMessage = statusText(for: normalizedWord, trigger: trigger)
        lastError = nil
        if preferences.autoSpeakEnabled {
            await speechService.speakWord(entry.word, preferences: preferences)
        }
        quickPopupController.show(
            entry: entry,
            onSpeakWord: { [weak self] in self?.speakCurrentWord() },
            onSpeakSentence: { [weak self] in self?.speakCurrentSentence() },
            onSave: { [weak self] in self?.saveCurrentWord() }
        )
    }

    func speakCurrentWord() {
        guard let word = currentEntry?.word else { return }
        Task {
            await speechService.speakWord(word, preferences: preferences)
        }
    }

    func speakCurrentSentence() {
        guard let sentence = currentEntry?.exampleSentence else { return }
        Task {
            await speechService.speakSentence(sentence, preferences: preferences)
        }
    }

    func saveCurrentWord() {
        guard let entry = currentEntry else { return }

        do {
            try favoritesStore.save(entry)
            studyRecords = studyStore.upsert(word: entry.word, into: studyRecords)
            try studyStore.save(studyRecords)
            statusMessage = "\"\(entry.word)\" saved to Markdown."
            lastError = nil
            loadSavedEntries()
        } catch {
            let message = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            lastError = message
            statusMessage = "Save failed."
        }
    }

    func markdownFilePath() -> URL {
        favoritesStore.fileURL
    }

    func openMarkdownFile() {
        NSWorkspace.shared.open(markdownFilePath())
    }

    func openGuide() {
        showingGuide = true
    }

    func closeGuide() {
        showingGuide = false
        preferences.onboardingCompleted = true
    }

    func hideQuickPopup() {
        quickPopupController.hide()
    }

    func quitApp() {
        quickPopupController.hide()
        AppInstanceManager.terminateAllInstancesAndCurrent()
    }

    func restartApp() {
        quickPopupController.hide()
        AppInstanceManager.restartCurrentApp()
    }

    func matchesSearch(_ entry: WordEntry, query: String) -> Bool {
        let normalizedQuery = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalizedQuery.isEmpty else { return true }

        return entry.word.localizedCaseInsensitiveContains(normalizedQuery)
            || entry.definition.localizedCaseInsensitiveContains(normalizedQuery)
            || entry.exampleSentence.localizedCaseInsensitiveContains(normalizedQuery)
    }

    func dueEntries() -> [WordEntry] {
        let dueWords = Set(studyRecords.filter(\.isDue).map(\.id))
        return recentSavedEntries.filter { dueWords.contains($0.word.lowercased()) }
    }

    func stats() -> LearningStats {
        studyStore.stats(entries: recentSavedEntries, records: studyRecords, dailyGoal: preferences.dailyGoal)
    }

    func applyReview(_ rating: ReviewRating, for entry: WordEntry) {
        do {
            studyRecords = studyStore.applyReview(rating, to: entry.word, in: studyRecords)
            try studyStore.save(studyRecords)
            statusMessage = "\"\(entry.word)\" scheduled again."
        } catch {
            lastError = error.localizedDescription
        }
    }

    func intervalText(for entry: WordEntry) -> String {
        guard let record = studyRecords.first(where: { $0.id == entry.word.lowercased() }) else {
            return "New"
        }

        if record.isDue {
            return "Due now"
        }

        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .short
        return formatter.localizedString(for: record.nextReviewAt, relativeTo: .now)
    }

    func refreshReminderPreference() {
        reminderScheduler.update(enabled: preferences.reminderEnabled)
    }

    private func loadSavedEntries() {
        recentSavedEntries = (try? favoritesStore.loadEntries()) ?? []
    }

    private func loadStudyRecords() {
        studyRecords = (try? studyStore.load()) ?? []
    }

    private func shouldAcceptCapture(word: String, trigger: CaptureTrigger) -> Bool {
        guard word.count <= 32 else { return false }
        guard word.rangeOfCharacter(from: CharacterSet.letters) != nil else { return false }

        if trigger == .selection {
            if word == lastCapturedWord && Date().timeIntervalSince(lastCaptureTime) < 1.2 {
                return false
            }
        }

        return true
    }

    private func statusText(for word: String, trigger: CaptureTrigger) -> String {
        switch trigger {
        case .selection:
            return "Selected \"\(word)\"."
        case .service:
            return "Opened \"\(word)\" from the context menu."
        case .manual, .hotKey:
            return "Captured \"\(word)\"."
        }
    }
}

enum AppError: LocalizedError {
    case invalidSelection
    case clipboardReadFailed

    var errorDescription: String? {
        switch self {
        case .invalidSelection:
            return "I couldn't find a clean word in the current selection."
        case .clipboardReadFailed:
            return "Copy the selected word once, or grant Accessibility permission and try again."
        }
    }
}

enum CaptureTrigger {
    case manual
    case hotKey
    case selection
    case service
}

final class HotKeyManager {
    private var hotKeyRef: EventHotKeyRef?
    private let handler: @Sendable () -> Void
    private var eventHandlerRef: EventHandlerRef?

    init(handler: @escaping @Sendable () -> Void) {
        self.handler = handler
    }

    func register() {
        var eventType = EventTypeSpec(eventClass: OSType(kEventClassKeyboard), eventKind: UInt32(kEventHotKeyPressed))
        InstallEventHandler(
            GetApplicationEventTarget(),
            { _, event, userData in
                guard let event else { return noErr }
                var hotKeyID = EventHotKeyID()
                let status = GetEventParameter(
                    event,
                    EventParamName(kEventParamDirectObject),
                    EventParamType(typeEventHotKeyID),
                    nil,
                    MemoryLayout<EventHotKeyID>.size,
                    nil,
                    &hotKeyID
                )

                guard status == noErr, hotKeyID.id == 1, let userData else { return noErr }
                let manager = Unmanaged<HotKeyManager>.fromOpaque(userData).takeUnretainedValue()
                manager.handler()
                return noErr
            },
            1,
            &eventType,
            UnsafeMutableRawPointer(Unmanaged.passUnretained(self).toOpaque()),
            &eventHandlerRef
        )

        let hotKeyID = EventHotKeyID(signature: OSType(0x57524459), id: 1)
        RegisterEventHotKey(
            UInt32(kVK_ANSI_G),
            UInt32(optionKey | cmdKey),
            hotKeyID,
            GetApplicationEventTarget(),
            0,
            &hotKeyRef
        )
    }
}

final class SelectionMonitor {
    private var globalMonitor: Any?
    private let handler: @Sendable () -> Void

    init(handler: @escaping @Sendable () -> Void) {
        self.handler = handler
    }

    func start() {
        globalMonitor = NSEvent.addGlobalMonitorForEvents(matching: [.leftMouseUp]) { [handler] _ in
            Task {
                try? await Task.sleep(for: .milliseconds(180))
                handler()
            }
        }
    }
}
