from django.db import models


class user(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    user_id = models.BigAutoField(db_column='user_id', primary_key=True)
    role = models.CharField(max_length=30)


class subject(models.Model):
    subject_name = models.CharField(max_length=30)
    subject_id = models.BigAutoField(db_column='subject_id', 	primary_key=True)


class exams(models.Model):
    exam_id = models.BigAutoField(db_column='exam_id', primary_key=True)
    exam_name = models.CharField(max_length=100)
    subject_id = models.ForeignKey(
        subject, on_delete=models.CASCADE, default='')


class question_set(models.Model):
    set_id = models.BigAutoField(db_column='set_id', primary_key=True)
    set_number = models.IntegerField(db_column='set_number', primary_key=False)
    subject_id = models.ForeignKey(subject, on_delete=models.CASCADE)
    exam_id = models.ForeignKey(exams, on_delete=models.CASCADE, default='')


class question(models.Model):
    question_id = models.BigAutoField(
        db_column='question_id', primary_key=True)
    question_number = models.BigIntegerField(
        db_column='question_number', 	primary_key=False)
    set_id = models.ForeignKey(question_set, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=300)


class answer(models.Model):
    answer_id = models.BigAutoField(db_column='answer_id', primary_key=True)
    question_id = models.ForeignKey(question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=3000)


class response(models.Model):
    response_id = models.BigAutoField(
        db_column='response_id', primary_key=True)
    question_id = models.ForeignKey(question, on_delete=models.CASCADE)
    response_text = models.CharField(max_length=3000)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)


class score(models.Model):
    score_id = models.BigAutoField(db_column='score_id', primary_key=True)
    score = models.FloatField()
    question_id = models.ForeignKey(question, on_delete=models.CASCADE)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
