import Foundation

struct FavoritesStore {
    let fileURL: URL

    init(fileURL: URL? = nil) {
        if let fileURL {
            self.fileURL = fileURL
        } else {
            self.fileURL = WordyDeskPaths.favoritesFileURL
        }
    }

    func save(_ entry: WordEntry) throws {
        let directoryURL = fileURL.deletingLastPathComponent()
        try FileManager.default.createDirectory(at: directoryURL, withIntermediateDirectories: true)

        if !FileManager.default.fileExists(atPath: fileURL.path) {
            try markdownHeader().write(to: fileURL, atomically: true, encoding: .utf8)
        }

        let currentContent = try String(contentsOf: fileURL, encoding: .utf8)
        guard !currentContent.localizedCaseInsensitiveContains("## \(entry.word)\n") else {
            return
        }

        let updatedContent = currentContent + entry.markdownBlock
        try updatedContent.write(to: fileURL, atomically: true, encoding: .utf8)
    }

    func loadEntries() throws -> [WordEntry] {
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            return []
        }

        let content = try String(contentsOf: fileURL, encoding: .utf8)
        let blocks = content.components(separatedBy: "\n## ").filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }

        return Array(blocks.compactMap { block in
            let normalizedBlock = block.hasPrefix("## ") ? block : "## " + block
            let lines = normalizedBlock.split(separator: "\n", omittingEmptySubsequences: false).map(String.init)

            guard let titleLine = lines.first, titleLine.hasPrefix("## ") else { return nil }
            let titleContent = String(titleLine.dropFirst(3))
            let parts = titleContent.components(separatedBy: " <sub>")
            let word = parts.first ?? titleContent
            let meaning = parts.count > 1
                ? parts[1].replacingOccurrences(of: "</sub>", with: "")
                : WordEntry.emptyDefinition
            let exampleLine = lines.first(where: { $0.hasPrefix("- Example: ") }) ?? ""
            let example = String(exampleLine.dropFirst(11))

            return WordEntry(
                word: word,
                definition: meaning,
                phonemes: WordEntry.emptyPronunciation,
                exampleSentence: example,
                createdAt: .now
            )
        }
        .reversed())
    }

    private func markdownHeader() -> String {
        """
        # WordyDesk Vocabulary Notebook

        A local Markdown notebook for words you collected on your Mac.

        """
    }
}
