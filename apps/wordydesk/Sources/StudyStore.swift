import Foundation

struct StudyStore {
    let fileURL: URL

    init(fileURL: URL? = nil) {
        if let fileURL {
            self.fileURL = fileURL
        } else {
            self.fileURL = WordyDeskPaths.studyProgressFileURL
        }
    }

    func load() throws -> [StudyRecord] {
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            return []
        }

        let data = try Data(contentsOf: fileURL)
        return try JSONDecoder.pretty.decode([StudyRecord].self, from: data)
    }

    func save(_ records: [StudyRecord]) throws {
        let directoryURL = fileURL.deletingLastPathComponent()
        try FileManager.default.createDirectory(at: directoryURL, withIntermediateDirectories: true)
        let data = try JSONEncoder.pretty.encode(records)
        try data.write(to: fileURL, options: .atomic)
    }

    func upsert(word: String, into records: [StudyRecord]) -> [StudyRecord] {
        var mutable = records
        if !mutable.contains(where: { $0.id == word.lowercased() }) {
            mutable.append(StudyRecord(word: word))
        }
        return mutable
    }

    func applyReview(_ rating: ReviewRating, to word: String, in records: [StudyRecord]) -> [StudyRecord] {
        var mutable = records
        guard let index = mutable.firstIndex(where: { $0.id == word.lowercased() }) else {
            return mutable
        }

        var record = mutable[index]
        let now = Date()
        let calendar = Calendar.current

        switch rating {
        case .again:
            record.reviewCount = max(record.reviewCount - 1, 0)
            record.intervalDays = 0.5
            record.easeFactor = max(1.8, record.easeFactor - 0.2)
            record.nextReviewAt = now.addingTimeInterval(12 * 60 * 60)
        case .good:
            record.reviewCount += 1
            record.intervalDays = nextInterval(for: record, multiplier: 1.0)
            record.nextReviewAt = calendar.date(byAdding: .day, value: max(Int(record.intervalDays.rounded()), 1), to: now) ?? now
        case .easy:
            record.reviewCount += 1
            record.easeFactor = min(2.8, record.easeFactor + 0.15)
            record.intervalDays = nextInterval(for: record, multiplier: 1.6)
            record.nextReviewAt = calendar.date(byAdding: .day, value: max(Int(record.intervalDays.rounded()), 2), to: now) ?? now
        }

        record.lastReviewedAt = now
        record.completedToday = calendar.isDateInToday(now)
        mutable[index] = record
        return mutable
    }

    func stats(entries: [WordEntry], records: [StudyRecord], dailyGoal: Int) -> LearningStats {
        let dueToday = records.filter(\.isDue).count
        let reviewedToday = records.filter { record in
            guard let lastReviewedAt = record.lastReviewedAt else { return false }
            return Calendar.current.isDateInToday(lastReviewedAt)
        }.count

        return LearningStats(
            totalSaved: entries.count,
            dueToday: dueToday,
            reviewedToday: reviewedToday,
            streakDays: streak(records: records),
            dailyGoal: dailyGoal
        )
    }

    private func nextInterval(for record: StudyRecord, multiplier: Double) -> Double {
        if record.reviewCount <= 1 { return 1 * multiplier }
        if record.reviewCount == 2 { return 3 * multiplier }
        return max(1, record.intervalDays * record.easeFactor * multiplier)
    }

    private func streak(records: [StudyRecord]) -> Int {
        let dates = Set(records.compactMap { record -> Date? in
            guard let lastReviewedAt = record.lastReviewedAt else { return nil }
            return Calendar.current.startOfDay(for: lastReviewedAt)
        })

        var streak = 0
        var cursor = Calendar.current.startOfDay(for: .now)

        while dates.contains(cursor) {
            streak += 1
            guard let previous = Calendar.current.date(byAdding: .day, value: -1, to: cursor) else { break }
            cursor = previous
        }

        return streak
    }
}

private extension JSONEncoder {
    static var pretty: JSONEncoder {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }
}

private extension JSONDecoder {
    static var pretty: JSONDecoder {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }
}
