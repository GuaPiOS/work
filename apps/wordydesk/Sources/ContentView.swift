import SwiftUI

struct ContentView: View {
    @Environment(\.openWindow) private var openWindow
    @EnvironmentObject private var appModel: AppModel
    @EnvironmentObject private var preferences: AppPreferences
    @State private var selectedTab = Tab.capture
    @State private var searchText = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            header

            Picker("View", selection: $selectedTab) {
                ForEach(Tab.allCases, id: \.self) { tab in
                    Text(tab.title).tag(tab)
                }
            }
            .pickerStyle(.segmented)

            switch selectedTab {
            case .capture:
                captureView
            case .review:
                reviewView
            case .progress:
                progressView
            }

            footer
        }
        .padding(22)
        .background(Color.white)
        .preferredColorScheme(.light)
        .popover(isPresented: $appModel.showingGuide, arrowEdge: .top) {
            OnboardingView {
                appModel.closeGuide()
            }
        }
    }

    private var header: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 5) {
                Text("WordyDesk")
                    .font(.system(size: 24, weight: .semibold))
                    .foregroundStyle(.black)
                Text("Silent English practice")
                    .font(.caption)
                    .foregroundStyle(.black.opacity(0.45))
            }

            Spacer()

            Button {
                appModel.openGuide()
            } label: {
                Image(systemName: "questionmark.circle")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(.black.opacity(0.55))
            }
            .buttonStyle(.plain)
        }
    }

    private var captureView: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 8) {
                Button("Capture") {
                    Task {
                        await appModel.captureSelectedWord(trigger: .manual)
                    }
                }
                .buttonStyle(.borderedProminent)
                .tint(.black)

                Button(preferences.autoSpeakEnabled ? "Auto Read" : "Manual Read") {
                    preferences.autoSpeakEnabled.toggle()
                }
                .buttonStyle(.bordered)
                .tint(.black)

                Button("Window") {
                    openWindow(id: "dashboard")
                }
                .buttonStyle(.bordered)
                .tint(.black)
            }

            Group {
                if let currentEntry = appModel.currentEntry {
                    heroCard(for: currentEntry)
                } else {
                    placeholderCard
                }
            }

            statusLine
        }
    }

    private var reviewView: some View {
        VStack(alignment: .leading, spacing: 12) {
            if !appModel.dueEntries().isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Due now")
                        .font(.headline)
                    ForEach(appModel.dueEntries().prefix(3)) { entry in
                        studyCard(for: entry)
                    }
                }
            }

            TextField("Search words", text: $searchText)
                .textFieldStyle(.roundedBorder)

            ScrollView {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(appModel.recentSavedEntries.filter { appModel.matchesSearch($0, query: searchText) }) { entry in
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text(entry.word)
                                    .font(.headline)
                                Spacer()
                                Text(appModel.intervalText(for: entry))
                                    .font(.caption)
                                    .foregroundStyle(.black.opacity(0.45))
                            }

                            Text(entry.definition)
                                .font(.caption)
                                .foregroundStyle(.black.opacity(0.55))
                                .lineLimit(1)

                            Text(entry.exampleSentence)
                                .font(.callout)
                                .foregroundStyle(.black.opacity(0.8))
                                .lineLimit(2)
                        }
                        .padding(14)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(surface)
                        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                    }
                }
            }
        }
    }

    private var progressView: some View {
        let stats = appModel.stats()

        return VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 10) {
                statCard(title: "Saved", value: "\(stats.totalSaved)")
                statCard(title: "Due", value: "\(stats.dueToday)")
                statCard(title: "Streak", value: "\(stats.streakDays)d")
            }

            VStack(alignment: .leading, spacing: 8) {
                Text("Daily plan")
                    .font(.headline)
                ProgressView(value: stats.completionRatio)
                    .tint(.black)
                Text("\(stats.reviewedToday) / \(stats.dailyGoal) reviewed")
                    .font(.caption)
                    .foregroundStyle(.black.opacity(0.55))
            }
            .padding(14)
            .background(surface)
            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))

            if let nextEntry = appModel.dueEntries().first {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Next")
                        .font(.headline)
                    Text(nextEntry.word)
                        .font(.title3.weight(.semibold))
                    Text(nextEntry.exampleSentence)
                        .foregroundStyle(.black.opacity(0.72))
                }
                .padding(14)
                .background(surface)
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }
        }
    }

    private var footer: some View {
        VStack(spacing: 10) {
            Divider()
            HStack {
                Button("Notebook") {
                    appModel.openMarkdownFile()
                }
                .buttonStyle(.plain)

                Spacer()

                Button("Restart") {
                    appModel.restartApp()
                }
                .buttonStyle(.plain)

                Button("Quit") {
                    appModel.quitApp()
                }
                .buttonStyle(.plain)
            }
            .font(.caption)
            .foregroundStyle(.black.opacity(0.5))
        }
    }

    private func heroCard(for entry: WordEntry) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                Text(entry.word)
                    .font(.system(size: 34, weight: .semibold))
                Spacer()
                Text(entry.definition)
                    .font(.caption)
                    .foregroundStyle(.black.opacity(0.45))
                    .lineLimit(2)
                    .multilineTextAlignment(.trailing)
                    .frame(maxWidth: 150)
            }

            Divider()

            Text(entry.exampleSentence)
                .font(.system(size: 18, weight: .regular))
                .foregroundStyle(.black.opacity(0.84))

            HStack(spacing: 8) {
                Button("Word") { appModel.speakCurrentWord() }
                Button("Example") { appModel.speakCurrentSentence() }
                Button("Save") { appModel.saveCurrentWord() }
            }
            .buttonStyle(.bordered)
            .tint(.black)
            .controlSize(.small)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.black)
        .foregroundStyle(.white)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var placeholderCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Select a word")
                .font(.title3.weight(.semibold))
                .foregroundStyle(.black)
            Text("The card will update when you capture a word.")
                .foregroundStyle(.black.opacity(0.45))
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(surface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var statusLine: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(appModel.statusMessage)
                .font(.caption)
                .foregroundStyle(.black.opacity(0.5))
            if let lastError = appModel.lastError {
                Text(lastError)
                    .font(.caption2)
                    .foregroundStyle(.red.opacity(0.8))
            }
        }
    }

    private func studyCard(for entry: WordEntry) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(entry.word)
                    .font(.headline)
                Spacer()
                Text(appModel.intervalText(for: entry))
                    .font(.caption)
                    .foregroundStyle(.black.opacity(0.45))
            }

            Text(entry.exampleSentence)
                .font(.callout)

            HStack(spacing: 8) {
                ForEach(ReviewRating.allCases, id: \.self) { rating in
                    Button(rating.title) {
                        appModel.applyReview(rating, for: entry)
                    }
                    .buttonStyle(.bordered)
                    .tint(.black)
                    .controlSize(.small)
                }
            }
        }
        .padding(14)
        .background(surface)
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private func statCard(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.black.opacity(0.45))
            Text(value)
                .font(.title3.weight(.semibold))
                .foregroundStyle(.black)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(surface)
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var surface: Color {
        Color.black.opacity(0.05)
    }
}

private enum Tab: CaseIterable {
    case capture
    case review
    case progress

    var title: String {
        switch self {
        case .capture:
            return "Now"
        case .review:
            return "Review"
        case .progress:
            return "Plan"
        }
    }
}
