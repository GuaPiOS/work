import Foundation

struct WordEntry: Identifiable, Equatable {
    let id = UUID()
    let word: String
    let definition: String
    let phonemes: String
    let exampleSentence: String
    let createdAt: Date

    var markdownBlock: String {
        return """
        ## \(word) <sub>\(definition)</sub>
        - Example: \(exampleSentence)

        """
    }
}

enum WordNormalizer {
    static func normalize(_ text: String) -> String {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        let tokens = trimmed.components(separatedBy: CharacterSet.whitespacesAndNewlines)

        let firstWord = tokens.first(where: { token in
            token.rangeOfCharacter(from: .letters) != nil
        }) ?? trimmed

        return firstWord
            .trimmingCharacters(in: CharacterSet.punctuationCharacters.union(.symbols))
            .lowercased()
    }
}

extension WordEntry {
    static let emptyDefinition = "No local dictionary definition was found for this word."
    static let emptyPronunciation = "American voice pronunciation available in app"
}

struct StudyRecord: Codable, Identifiable, Equatable {
    let id: String
    let word: String
    var reviewCount: Int
    var intervalDays: Double
    var easeFactor: Double
    var lastReviewedAt: Date?
    var nextReviewAt: Date
    var createdAt: Date
    var completedToday: Bool

    init(word: String, createdAt: Date = .now) {
        self.id = word.lowercased()
        self.word = word
        self.reviewCount = 0
        self.intervalDays = 0
        self.easeFactor = 2.3
        self.lastReviewedAt = nil
        self.nextReviewAt = createdAt
        self.createdAt = createdAt
        self.completedToday = false
    }

    var isDue: Bool {
        nextReviewAt <= .now
    }
}

enum ReviewRating: String, Codable, CaseIterable {
    case again
    case good
    case easy

    var title: String {
        switch self {
        case .again:
            return "Again"
        case .good:
            return "Good"
        case .easy:
            return "Easy"
        }
    }
}

struct LearningStats {
    let totalSaved: Int
    let dueToday: Int
    let reviewedToday: Int
    let streakDays: Int
    let dailyGoal: Int

    var completionRatio: Double {
        guard dailyGoal > 0 else { return 0 }
        return min(Double(reviewedToday) / Double(dailyGoal), 1)
    }
}
