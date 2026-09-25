class AdminService:

    def show_dashboard(self, user):
        while True:
            print("\n================================")
            print("         ADMIN DASHBOARD")
            print("================================")
            print("Welcome,", user.get_full_name())
            print()
            print("1. View Profile")
            print("2. Manage Students")
            print("3. Manage Faculty")
            print("4. Manage Courses")
            print("5. Manage Subjects")
            print("6. Manage Notices")
            print("7. Manage Leave Requests")
            print("8. Manage Placement")
            print("9. Logout")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                user.display_info()

            elif choice == "2":
                print("\nStudent management will be added next.")

            elif choice == "3":
                print("\nFaculty management will be added next.")

            elif choice == "4":
                print("\nCourse management will be added next.")

            elif choice == "5":
                print("\nSubject management will be added next.")

            elif choice == "6":
                print("\nNotice management will be added next.")

            elif choice == "7":
                print("\nLeave management will be added next.")

            elif choice == "8":
                print("\nPlacement management will be added next.")

            elif choice == "9":
                print("\nLogging out...")
                break

            else:
                print("\nInvalid choice. Please try again.")