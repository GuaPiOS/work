import Foundation

struct ExampleSentenceGenerator {
    private let templates = [
        "I heard \"\(Placeholder.word)\" today.",
        "People say \"\(Placeholder.word)\" a lot.",
        "I learned \"\(Placeholder.word)\" this morning.",
        "I saw \"\(Placeholder.word)\" in a short video.",
        "My friend used \"\(Placeholder.word)\" just now."
    ]

    func makeSentence(for word: String) -> String {
        let seed = abs(word.hashValue)
        let template = templates[seed % templates.count]
        return template.replacingOccurrences(of: Placeholder.word, with: word)
    }

    private enum Placeholder {
        static let word = "{word}"
    }
}
