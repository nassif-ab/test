
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from crud import get_users, get_user_by_username, get_user_by_email, create_user
from schemas import UserCreate
import time

# استيراد بيانات المستخدمين من ملف data_users.py
from data_users import data_users, create_or_update_user

def get_categories_from_db(db: Session):
    """استرجاع التصنيفات من قاعدة البيانات"""
    print("جلب التصنيفات من قاعدة البيانات...")
    categories = []
    
    # استرجاع جميع التصنيفات الفريدة من جدول المنشورات
    db_categories = db.query(models.Post.categorie).distinct().all()
    
    # تحويل النتيجة إلى قائمة بسيطة
    for category in db_categories:
        categories.append(category[0])
    
    print(f"✅ تم العثور على {len(categories)} تصنيف في قاعدة البيانات")
    return categories

def get_random_date(start_date, end_date):
    """إنشاء تاريخ عشوائي بين تاريخ البداية وتاريخ النهاية"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def assign_user_interests(db: Session, categories):
    """تعيين ثلاث تصنيفات اهتمام لكل مستخدم بمستويات تفاعل مختلفة"""
    print("تعيين اهتمامات مخصصة للمستخدمين...")
    
    # الحصول على جميع المستخدمين والمنشورات حسب التصنيف
    users = db.query(models.User).all()
    
    # إنشاء قاموس لتخزين المنشورات حسب التصنيف
    posts_by_category = {}
    for category in categories:
        posts_by_category[category] = db.query(models.Post).filter(models.Post.categorie == category).all()
    
    # إزالة التصنيفات التي ليس لها منشورات
    categories_with_posts = [cat for cat in categories if posts_by_category[cat]]
    
    if not categories_with_posts:
        print("لا توجد تصنيفات بها منشورات لتعيين اهتمامات")
        return
    
    # لكل مستخدم، تعيين ثلاث فئات اهتمام بمستويات مختلفة
    for user in users:
        print(f"تعيين اهتمامات للمستخدم: {user.username}")
        
        # تحديد ثلاث تصنيفات مختلفة عشوائيًا
        if len(categories_with_posts) >= 3:
            user_categories = random.sample(categories_with_posts, 3)
        else:
            # إذا كان هناك أقل من 3 تصنيفات، استخدم المتاحة وكرر إذا لزم الأمر
            user_categories = categories_with_posts.copy()
            while len(user_categories) < 3:
                user_categories.append(random.choice(categories_with_posts))
        
        # المستوى 1: تفاعل عالي - زيارات وإعجابات كثيرة
        high_interest_category = user_categories[0]
        # المستوى 2: اهتمام متوسط - زيارات متكررة، إعجابات قليلة
        medium_interest_category = user_categories[1]
        # المستوى 3: اهتمام منخفض - زيارات قليلة، بدون إعجابات
        low_interest_category = user_categories[2]
        
        # حفظ اهتمامات المستخدم للرجوع إليها
        user_interests = {
            "high_interest": high_interest_category,
            "medium_interest": medium_interest_category,
            "low_interest": low_interest_category
        }
        
        # طباعة للتصحيح
        print(f"  - اهتمام عالي: {high_interest_category}")
        print(f"  - اهتمام متوسط: {medium_interest_category}")
        print(f"  - اهتمام منخفض: {low_interest_category}")
    
    print("✅ تم تعيين الاهتمامات لجميع المستخدمين")
    return users

def generate_personalized_visits_and_likes(db: Session, categories, start_date=None, end_date=None):
    """إنشاء زيارات وإعجابات مخصصة وفقًا لاهتمامات كل مستخدم"""
    print("إنشاء تفاعلات مخصصة حسب الاهتمامات...")
    
    # إعداد التواريخ
    if start_date is None:
        start_date = datetime.now() - timedelta(days=180)
    if end_date is None:
        end_date = datetime.now()
    
    # تعيين الاهتمامات والحصول على المستخدمين
    users = assign_user_interests(db, categories)
    if not users:
        print("لا يوجد مستخدمين لإنشاء تفاعلات")
        return
    
    # إنشاء قاموس لتخزين المنشورات حسب التصنيف
    posts_by_category = {}
    for category in categories:
        posts_by_category[category] = db.query(models.Post).filter(models.Post.categorie == category).all()
    
    # مجموعة لتجنب التكرار في الإعجابات
    existing_likes = set()
    likes = db.query(models.Like).all()
    for like in likes:
        existing_likes.add((like.user_id, like.post_id))
    
    # إنشاء تفاعلات لكل مستخدم
    visits_created = 0
    likes_created = 0
    
    for user in users:
        print(f"إنشاء تفاعلات لـ {user.username}...")
        
        # تحديد ثلاث تصنيفات مختلفة عشوائيًا للمستخدم
        categories_with_available_posts = [cat for cat in categories if posts_by_category[cat]]
        if len(categories_with_available_posts) >= 3:
            selected_categories = random.sample(categories_with_available_posts, 3)
        else:
            selected_categories = categories_with_available_posts.copy()
            while len(selected_categories) < 3:
                selected_categories.append(random.choice(categories_with_available_posts))
        
        # المستوى 1: تفاعل عالي (زيارات وإعجابات كثيرة)
        high_interest_category = selected_categories[0]
        high_interest_posts = posts_by_category[high_interest_category]
        
        # إنشاء 15-25 زيارة لتصنيف الاهتمام العالي
        if high_interest_posts:
            num_visits = random.randint(15, 25)
            for _ in range(num_visits):
                post = random.choice(high_interest_posts)
                visit = models.Visit(
                    post_id=post.id,
                    user_id=user.id,
                    ip_address=f"192.168.1.{random.randint(1, 255)}",
                    visit_date=get_random_date(start_date, end_date)
                )
                db.add(visit)
                visits_created += 1
            
            # إنشاء 10-15 إعجاب لتصنيف الاهتمام العالي
            num_likes = random.randint(10, 15)
            like_attempts = 0
            likes_added = 0
            
            while likes_added < num_likes and like_attempts < num_likes * 2:
                like_attempts += 1
                post = random.choice(high_interest_posts)
                
                # التحقق مما إذا كان هذا الإعجاب موجودًا بالفعل
                if (user.id, post.id) in existing_likes:
                    continue
                
                like = models.Like(
                    user_id=user.id,
                    post_id=post.id,
                    created_at=get_random_date(start_date, end_date)
                )
                db.add(like)
                existing_likes.add((user.id, post.id))
                likes_created += 1
                likes_added += 1
        
        # المستوى 2: اهتمام متوسط (زيارات متكررة، إعجابات قليلة)
        if len(selected_categories) > 1:
            medium_interest_category = selected_categories[1]
            medium_interest_posts = posts_by_category[medium_interest_category]
            
            # إنشاء 8-12 زيارة لتصنيف الاهتمام المتوسط
            if medium_interest_posts:
                num_visits = random.randint(8, 12)
                for _ in range(num_visits):
                    post = random.choice(medium_interest_posts)
                    visit = models.Visit(
                        post_id=post.id,
                        user_id=user.id,
                        ip_address=f"192.168.1.{random.randint(1, 255)}",
                        visit_date=get_random_date(start_date, end_date)
                    )
                    db.add(visit)
                    visits_created += 1
                
                # إنشاء 2-4 إعجابات لتصنيف الاهتمام المتوسط
                num_likes = random.randint(2, 4)
                like_attempts = 0
                likes_added = 0
                
                while likes_added < num_likes and like_attempts < num_likes * 2:
                    like_attempts += 1
                    post = random.choice(medium_interest_posts)
                    
                    # التحقق مما إذا كان هذا الإعجاب موجودًا بالفعل
                    if (user.id, post.id) in existing_likes:
                        continue
                    
                    like = models.Like(
                        user_id=user.id,
                        post_id=post.id,
                        created_at=get_random_date(start_date, end_date)
                    )
                    db.add(like)
                    existing_likes.add((user.id, post.id))
                    likes_created += 1
                    likes_added += 1
        
        # المستوى 3: اهتمام منخفض (زيارات قليلة، بدون إعجابات)
        if len(selected_categories) > 2:
            low_interest_category = selected_categories[2]
            low_interest_posts = posts_by_category[low_interest_category]
            
            # إنشاء 1-3 زيارات لتصنيف الاهتمام المنخفض
            if low_interest_posts:
                num_visits = random.randint(1, 3)
                for _ in range(num_visits):
                    post = random.choice(low_interest_posts)
                    visit = models.Visit(
                        post_id=post.id,
                        user_id=user.id,
                        ip_address=f"192.168.1.{random.randint(1, 255)}",
                        visit_date=get_random_date(start_date, end_date)
                    )
                    db.add(visit)
                    visits_created += 1
        
        # الالتزام لكل مستخدم لتجنب مشاكل الذاكرة
        db.commit()
    
    print(f"✅ تم إنشاء {visits_created} زيارة مخصصة")
    print(f"✅ تم إنشاء {likes_created} إعجاب مخصص")

def create_users_from_data(db: Session):
    """إنشاء أو تحديث المستخدمين من البيانات المستوردة"""
    print("إنشاء أو تحديث المستخدمين...")
    
    users_created = 0
    users_updated = 0
    
    for data in data_users:
        user_data = {
            "username": data["username"],
            "fullName": data["fullName"],
            "email": data["email"],
            "password": "123456789",
            "is_admin": False
        }
        
        # إنشاء أو تحديث المستخدم
        user, action = create_or_update_user(db, user_data)
        
        if action == "creado":
            users_created += 1
        else:
            users_updated += 1
    
    print(f"✅ تم إنشاء {users_created} مستخدم وتحديث {users_updated} مستخدم")

def clean_existing_interactions(db: Session):
    """مسح التفاعلات الموجودة لإنشاء تفاعلات جديدة"""
    print("مسح التفاعلات الموجودة...")
    
    # حذف الإعجابات والزيارات الموجودة
    db.query(models.Like).delete()
    db.query(models.Visit).delete()
    db.commit()
    
    print("✅ تم حذف التفاعلات الموجودة")

def main():
    # إنشاء جلسة قاعدة بيانات
    db = SessionLocal()
    
    try:
        # تحديد نطاق تواريخ مخصص (آخر 3 أشهر افتراضيًا)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # 3 أشهر
        
        # السماح بتخصيص نطاق التواريخ من سطر الأوامر
        import sys
        if len(sys.argv) > 2:
            try:
                # التنسيق المتوقع: YYYY-MM-DD
                start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
                end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
                print(f"استخدام نطاق تواريخ مخصص: {start_date.strftime('%Y-%m-%d')} إلى {end_date.strftime('%Y-%m-%d')}")
            except ValueError:
                print("تنسيق التاريخ غير صحيح. استخدام القيم الافتراضية.")
                print("التنسيق الصحيح: python generate_personalized_data.py 2025-01-01 2025-05-01")
        
        # إنشاء أو تحديث المستخدمين
        create_users_from_data(db)
        
        # مسح التفاعلات الموجودة (اختياري - قم بإلغاء التعليق إذا كنت تريد حذف البيانات الموجودة)
        clean_existing_interactions(db)
        
        # جلب التصنيفات من قاعدة البيانات
        categories = get_categories_from_db(db)
        
        # إنشاء تفاعلات مخصصة وفقًا للاهتمامات
        generate_personalized_visits_and_likes(db, categories, start_date=start_date, end_date=end_date)
        
        # تدريب نظام التوصية
        print("\nتم إنشاء بيانات مخصصة بنجاح.")
        print("لتحسين التوصيات، قم بتشغيل سكريبت التدريب:")
        print("  python scheduled_training.py")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات المخصصة: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # إغلاق الجلسة
        db.close()

if __name__ == "__main__":
    main()