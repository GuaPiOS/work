import Foundation
import UserNotifications

@MainActor
final class ReminderScheduler {
    func update(enabled: Bool) {
        if enabled {
            requestAndSchedule()
        } else {
            UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: [notificationID])
        }
    }

    private func requestAndSchedule() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { granted, _ in
            guard granted else { return }

            var dateComponents = DateComponents()
            dateComponents.hour = 20
            dateComponents.minute = 30

            let content = UNMutableNotificationContent()
            content.title = "WordyDesk review"
            content.body = "A few words are waiting for your next review."
            content.sound = .default

            let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
            let request = UNNotificationRequest(identifier: self.notificationID, content: content, trigger: trigger)
            UNUserNotificationCenter.current().add(request)
        }
    }

    private let notificationID = "wordydesk.dailyReview"
}
