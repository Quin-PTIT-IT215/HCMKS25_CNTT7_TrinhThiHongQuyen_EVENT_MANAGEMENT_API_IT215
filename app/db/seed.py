from datetime import datetime, timezone
import bcrypt
from app.db.database import SessionLocal
from app.models.user import User
from app.models.event import Event, EventStaff
from app.models.event_task import EventTask


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def seed_data():
    db = SessionLocal()
    try:

        admin = User(
            email="admin@gmail.com",
            password_hash=hash_password("123456"),
            full_name="Admin",
            role="Admin",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        user1 = User(
            email="user1@gmail.com",
            password_hash=hash_password("123456"),
            full_name="Nguyễn Văn A",
            role="User",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        user2 = User(
            email="user2@gmail.com",
            password_hash=hash_password("123456"),
            full_name="Trần Thị B",
            role="User",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        user3 = User(
        email="user3@gmail.com",
        password_hash=hash_password("123456"),
        full_name="Lê Văn C",
        role="User",
        is_active=True,
        created_at=datetime.now(timezone.utc)
        )

        user4 = User(
            email="user4@gmail.com",
            password_hash=hash_password("123456"),
            full_name="Phạm Thị D",
            role="User",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        user5 = User(
            email="user5@gmail.com",
            password_hash=hash_password("123456"),
            full_name="Hoàng Văn E",
            role="User",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        db.add_all([
            admin,
            user1,
            user2,
            user3,
            user4,
            user5
        ])

        db.commit()
        db.refresh(admin)
        db.refresh(user1)
        db.refresh(user2)
        db.refresh(user3)
        db.refresh(user4)
        db.refresh(user5)


        event1 = Event(
            name="Workshop FastAPI",
            description="Workshop học FastAPI",
            owner_id=admin.id,
            created_at=datetime.now(timezone.utc)
        )

        event2 = Event(
            name="Team Building 2026",
            description="Sự kiện team building",
            owner_id=user1.id,
            created_at=datetime.now(timezone.utc)
        )

        event3 = Event(
            name="Seminar Công nghệ 2026",
            description="Seminar chia sẻ kiến thức công nghệ",
            owner_id=user2.id,
            created_at=datetime.now(timezone.utc)
        )

        event4 = Event(
            name="Hackathon IT215",
            description="Cuộc thi lập trình dành cho sinh viên",
            owner_id=user3.id,
            created_at=datetime.now(timezone.utc)
        )

        event5 = Event(
            name="Sinh nhật công ty",
            description="Sự kiện sinh nhật công ty năm 2026",
            owner_id=user4.id,
            created_at=datetime.now(timezone.utc)
        )

        db.add_all([
            event1,
            event2,
            event3,
            event4,
            event5
        ])

        db.commit()
        db.refresh(event1)
        db.refresh(event2)
        db.refresh(event3)
        db.refresh(event4)
        db.refresh(event5)


        staff1 = EventStaff(
            event_id=event1.id,
            user_id=admin.id,
            role="Owner",
            joined_at=datetime.now(timezone.utc)
        )

        staff2 = EventStaff(
            event_id=event1.id,
            user_id=user1.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        staff3 = EventStaff(
            event_id=event2.id,
            user_id=user1.id,
            role="Owner",
            joined_at=datetime.now(timezone.utc)
        )

        staff4 = EventStaff(
            event_id=event2.id,
            user_id=user2.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        staff5 = EventStaff(
            event_id=event3.id,
            user_id=user2.id,
            role="Owner",
            joined_at=datetime.now(timezone.utc)
        )

        staff6 = EventStaff(
            event_id=event3.id,
            user_id=user3.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        staff7 = EventStaff(
            event_id=event3.id,
            user_id=user4.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        staff8 = EventStaff(
            event_id=event4.id,
            user_id=user3.id,
            role="Owner",
            joined_at=datetime.now(timezone.utc)
        )

        staff9 = EventStaff(
            event_id=event4.id,
            user_id=user1.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        staff10 = EventStaff(
            event_id=event4.id,
            user_id=user5.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        staff11 = EventStaff(
            event_id=event5.id,
            user_id=user4.id,
            role="Owner",
            joined_at=datetime.now(timezone.utc)
        )

        staff12 = EventStaff(
            event_id=event5.id,
            user_id=user2.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        staff13 = EventStaff(
            event_id=event5.id,
            user_id=user5.id,
            role="Member",
            joined_at=datetime.now(timezone.utc)
        )

        db.add_all([
            staff1,
            staff2,
            staff3,
            staff4,
            staff5,
            staff6,
            staff7,
            staff8,
            staff9,
            staff10,
            staff11,
            staff12,
            staff13
        ])

        db.commit()

        task1 = EventTask(
            event_id=event1.id,
            title="Chuẩn bị slide",
            description="Chuẩn bị slide cho workshop",
            assignee_id=user1.id,
            status="Todo",
            priority="High",
            due_date=None,
            created_at=datetime.now(timezone.utc)
        )

        task2 = EventTask(
            event_id=event1.id,
            title="Chuẩn bị phòng",
            description="Kiểm tra phòng tổ chức",
            assignee_id=user1.id,
            status="In_progress",
            priority="Medium",
            due_date=None,
            created_at=datetime.now(timezone.utc)
        )

        task3 = EventTask(
            event_id=event2.id,
            title="Chuẩn bị banner",
            description="Thiết kế banner team building",
            assignee_id=user2.id,
            status="Todo",
            priority="Low",
            due_date=None,
            created_at=datetime.now(timezone.utc)
        )

        task4 = EventTask(
            event_id=event2.id,
            title="Lên danh sách thành viên",
            description="Tổng hợp danh sách thành viên tham gia",
            assignee_id=user1.id,
            status="Done",
            priority="High",
            due_date=datetime(2026, 9, 1, tzinfo=timezone.utc),
            created_at=datetime.now(timezone.utc)
        )

        task5 = EventTask(
            event_id=event2.id,
            title="Đặt xe di chuyển",
            description="Liên hệ và đặt xe cho thành viên",
            assignee_id=user2.id,
            status="In_progress",
            priority="High",
            due_date=datetime(2026, 9, 5, tzinfo=timezone.utc),
            created_at=datetime.now(timezone.utc)
        )

        task6 = EventTask(
            event_id=event3.id,
            title="Chuẩn bị nội dung seminar",
            description="Chuẩn bị nội dung trình bày",
            assignee_id=user3.id,
            status="Todo",
            priority="High",
            due_date=datetime(2026, 9, 10, tzinfo=timezone.utc),
            created_at=datetime.now(timezone.utc)
        )

        task7 = EventTask(
            event_id=event3.id,
            title="Thiết kế poster",
            description="Thiết kế poster quảng bá seminar",
            assignee_id=user4.id,
            status="Done",
            priority="Medium",
            due_date=datetime(2026, 9, 3, tzinfo=timezone.utc),
            created_at=datetime.now(timezone.utc)
        )

        task8 = EventTask(
            event_id=event4.id,
            title="Chuẩn bị đề bài",
            description="Chuẩn bị đề bài cho Hackathon",
            assignee_id=user3.id,
            status="In_progress",
            priority="High",
            due_date=datetime(2026, 9, 15, tzinfo=timezone.utc),
            created_at=datetime.now(timezone.utc)
        )

        task9 = EventTask(
            event_id=event4.id,
            title="Chuẩn bị phòng thi",
            description="Kiểm tra phòng và thiết bị",
            assignee_id=user1.id,
            status="Todo",
            priority="Medium",
            due_date=None,
            created_at=datetime.now(timezone.utc)
        )

        task10 = EventTask(
            event_id=event5.id,
            title="Trang trí sân khấu",
            description="Chuẩn bị và trang trí sân khấu",
            assignee_id=user4.id,
            status="Todo",
            priority="Low",
            due_date=datetime(2026, 10, 1, tzinfo=timezone.utc),
            created_at=datetime.now(timezone.utc)
        )

        task11 = EventTask(
            event_id=event5.id,
            title="Chuẩn bị âm thanh",
            description="Kiểm tra hệ thống âm thanh",
            assignee_id=user5.id,
            status="Done",
            priority="Medium",
            due_date=datetime(2026, 9, 28, tzinfo=timezone.utc),
            created_at=datetime.now(timezone.utc)
        )


        db.add_all([
            task1,
            task2,
            task3,
            task4,
            task5,
            task6,
            task7,
            task8,
            task9,
            task10,
            task11
        ])

        db.commit()

        print("Seed dữ liệu thành công!")

    except Exception as e:

        db.rollback()

        print("Seed dữ liệu thất bại:")
        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    seed_data()