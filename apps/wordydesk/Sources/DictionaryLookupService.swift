import CoreServices
import Foundation

struct DictionaryLookupService {
    func definition(for word: String) -> String {
        let nsWord = word as NSString
        let range = CFRange(location: 0, length: nsWord.length)

        guard let result = DCSCopyTextDefinition(nil, word as CFString, range)?.takeRetainedValue() as String? else {
            return WordEntry.emptyDefinition
        }

        let cleaned = result
            .replacingOccurrences(of: "\n\n", with: "\n")
            .trimmingCharacters(in: CharacterSet.whitespacesAndNewlines)

        guard !cleaned.isEmpty else { return WordEntry.emptyDefinition }

        let firstLine = cleaned.components(separatedBy: .newlines).first ?? cleaned
        let firstSentence = firstLine.components(separatedBy: ". ").first ?? firstLine
        let concise = firstSentence
            .replacingOccurrences(of: "  ", with: " ")
            .trimmingCharacters(in: .whitespacesAndNewlines)

        return concise.isEmpty ? WordEntry.emptyDefinition : concise
    }
}
