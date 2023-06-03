from django.shortcuts import render, redirect, get_list_or_404
from django.http import HttpResponse
from database.models import user
from database.models import subject, exams, score, question_set, question, response, answer
from django.db import connection
from operator import itemgetter
from django.contrib import messages
from . import jaro, leven, jaccard, cosine, hamming
import nltk
import string
from nltk.tokenize import word_tokenize
from scipy.spatial.distance import hamming
from Levenshtein import distance
from nltk.corpus import stopwords

# jaccard
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import FunctionTransformer
import string
from scipy.spatial import distance
# cosine
from sklearn.metrics.pairwise import cosine_similarity

# ----


import math

uname = ""
q_id = 0
session_teacher = ['false']
session_student = ['false']

homepage_teacher = ['false']
homepage_student = ['false']

# create another row to check wheather a student has already taken an exam


# Create your views here.

def homepage(request):
    if homepage_teacher[0] == "false" and homepage_student[0] == "false":
        return render(request, 'login/homepage.html')

    elif homepage_teacher[0] == "true":
        session_teacher.insert(0, "true")
        messages.info(
            request, 'You are already logged in so you can not go to the homepage,inorder to access the homepage please logout!')
        return redirect('/teacher/dashboard/')

    elif homepage_student[0] == "true":
        session_student.insert(0, "true")
        messages.info(
            request, 'You are already logged in so you can not go to the homepage,inorder to access the homepage please logout!')
        return redirect('/student/dashboard/')

    else:
        print("value of homepage_student", homepage_student)
        return render(request, 'login/homepage.html')


def login_teacher(request):

    # first query to get the username from the database
    query = """     
          SELECT username FROM `database_user` 
            """
    data = []
    # connect with the database
    with connection.cursor() as cursor:
        cursor.execute(query)
        #   data = cursor.fetchall()
    for i in cursor:
        data.append(i)

    # print("the value is:",data)

    # Second query to get the password from the database
    query1 = """     
           SELECT password
           FROM `database_user`  
            """
    data1 = []
    with connection.cursor() as cursor1:
        cursor1.execute(query1)
        #   data1 = cursor1.fetchall()

    for j in cursor1:
        data1.append(j)
    # print("the password is:",data1)

    # third query to get the role from the database
    query2 = """     
          SELECT role FROM `database_user`
            """
    data2 = []
    with connection.cursor() as cursor2:
        cursor2.execute(query2)

    for l in cursor2:
        data2.append(l)

    res = list(map(itemgetter(0), data))
    res1 = list(map(itemgetter(0), data1))
    res2 = list(map(itemgetter(0), data2))

    # print("the res list",res)
    # print("the res1 list",res1)
    # print("the rest2",res2)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        global uname
        uname = username
        # print("the user name is",username)
        # print("the password is",password)

        i = 0
        k = len(res)
        while i < k:
            if res2[i] == "teacher" or res2[i] == "Teacher":
                if res[i] == username and res1[i] == password:
                    session_teacher.insert(0, "true")
                    return redirect('/teacher/dashboard/')
                    break
            i = i+1

        else:
            messages.info(
                request, 'Make sure you choose the right login! Invalid username or password!')
            return redirect('/teacher/login/')

    if homepage_teacher[0] == "false" and homepage_student[0] == "false":
        return render(request, 'login/login_teacher.html')
    elif homepage_teacher[0] == "true":
        messages.info(
            request, 'You are already logged in so you can not go to the teacher login page,inorder to access the login page please logout!')
        return redirect('/teacher/dashboard/')
    else:
        messages.info(
            request, 'You are already logged in so you can not go to the teacher login page,inorder to access the login page please logout!')
        return redirect('/student/dashboard/')


def login_student(request):
    # first query to get the username from the database
    query = """     
          SELECT username FROM `database_user` 
            """
    data = []
    # connect with the database
    with connection.cursor() as cursor:
        cursor.execute(query)
        #   data = cursor.fetchall()
    for i in cursor:
        data.append(i)

    # print("the value is:",data)

    # Second query to get the password from the database
    query1 = """     
           SELECT password
           FROM `database_user`  
            """
    data1 = []
    with connection.cursor() as cursor1:
        cursor1.execute(query1)
        #   data1 = cursor1.fetchall()

    for j in cursor1:
        data1.append(j)
    # print("the password is:",data1)

    # third query to get the role from the database
    query2 = """     
          SELECT role FROM `database_user`
            """
    data2 = []
    with connection.cursor() as cursor2:
        cursor2.execute(query2)

    for l in cursor2:
        data2.append(l)

    res = list(map(itemgetter(0), data))
    res1 = list(map(itemgetter(0), data1))
    res2 = list(map(itemgetter(0), data2))

    # print("the res list",res)
    # print("the res1 list",res1)
    print("the rest2", res2)

    if request.method == "POST":
        username1 = request.POST['username1']
        password1 = request.POST['password1']
        global uname
        uname = username1

        # print("the user name is",username)
        # print("the password is",password)

        i = 0
        k = len(res)
        while i < k:
            if res2[i] == "student" or res2[i] == "Student":
                if res[i] == username1 and res1[i] == password1:
                    session_student.insert(0, "true")
                    return redirect('/student/dashboard/')
                    break
            i = i+1

        else:
            messages.info(
                request, 'Make sure you choose the right login! Invalid username or password!')
            return redirect('/student/login/')

    if homepage_student[0] == "false" and homepage_teacher[0] == "false":
        return render(request, 'login/login_student.html')
    elif homepage_student[0] == "true":
        messages.info(
            request, 'You are already logged in so you can not go to the login page,inorder to access the login page please logout!')
        return redirect('/student/dashboard/')
    else:
        messages.info(
            request, 'You are already logged in so you can not go to the student login page,inorder to access the login page please logout!')
        return redirect('/teacher/dashboard/')

# teacher dashboard --------------->


def teacher_dashboard(request):
    subs = subject.objects.all()
    global uname
    uname = uname.title()
    if session_teacher[0] == "true":
        homepage_teacher.insert(0, "true")
        return render(request, 'courses/course_list.html', {'subs': subs, 'uname': uname})
    else:
        return redirect('/')


def course_detail(request, subject_id):
   #  subs = subject.objects.all()
    sub = get_list_or_404(subject, subject_id=subject_id)
    xms = get_list_or_404(exams, subject_id_id=subject_id)
    # print(subject_id)
    context = {
        'sub': sub,
        'subject_id': subject_id,
        'xms': xms,
    }
    if session_teacher[0] == "true":
        homepage_teacher.insert(0, "true")
        return render(request, 'courses/course_details.html', context)
    else:
        return redirect('/')

    if homepage_teacher[0] == "false" and homepage_student[0] == "false":
        return render(request, 'login/login_teacher.html')
    elif homepage_teacher[0] == "true":
        messages.info(
            request, 'You are already logged in so you can not go to the teacher login page,inorder to access the login page please logout!')
        return redirect('/teacher/dashboard/')
    else:
        messages.info(
            request, 'You are already logged in so you can not go to the teacher login page,inorder to access the login page please logout!')
        return redirect('/teacher/dashboard/')


def student_dashboard(request):
    subs = subject.objects.all()
    global uname
    uname = uname.title()
    if session_student[0] == "true":
        homepage_student.insert(0, "true")
        return render(request, 'courses/st_course_list.html', {'subs': subs, 'uname': uname})
    else:
        return redirect('/')


# def course_detail(request, subject_id):
#    #  subs = subject.objects.all()
#     sub = get_list_or_404(subject, subject_id=subject_id)
#     if session_teacher[0] == "true":
#         homepage_teacher.insert(0, "true")
#         return render(request, 'courses/course_details.html', {'sub': sub})
#     else:
#         return redirect('/')


def st_course_detail(request, subject_id):
   #  subs = subject.objects.all()
    sub = get_list_or_404(subject, subject_id=subject_id)
    xms = get_list_or_404(exams, subject_id_id=subject_id)
    # print(subject_id)
    global uname
    uname = uname.title()
    context = {
        'sub': sub,
        'subject_id': subject_id,
        'xms': xms,
        'uname': uname,
    }
    if session_student[0] == "true":
        homepage_student.insert(0, "true")
        return render(request, 'courses/st_course_details.html', context)
    else:
        return redirect('/')

    # if homepage_teacher[0] == "false" and homepage_student[0] == "false":
    #     return render(request, 'login/login_teacher.html')
    # elif homepage_teacher[0] == "true":
    #     messages.info(
    #         request, 'You are already logged in so you can not go to the teacher login page,inorder to access the login page please logout!')
    #     return redirect('/student/dashboard/')
    # else:
    #     messages.info(
    #         request, 'You are already logged in so you can not go to the teacher login page,inorder to access the login page please logout!')
    #     return redirect('/student/dashboard/')


def save_exam_id(exam_id):
    return exam_id


def create_exam(request, subject_id):

    subs = subject.objects.all()
    sub = get_list_or_404(subject, subject_id=subject_id)
    sub = sub[0]

    context = {
        'subject_id': subject_id,
        'sub': sub,
    }
    if request.method == 'POST':
        exam_id = request.POST['exam_id']
        exam_name = request.POST['exam_name']

        # create exam obj
        exam = exams.objects.create(subject_id_id=subject_id,
                                    exam_id=exam_id, exam_name=exam_name)
        exam.save()
        save_exam_id(exam_id)
        # redirect to a success page
        return redirect('login:create_set', subject_id=subject_id, exam_id=exam_id)

    if session_teacher[0] == "true":
        homepage_teacher.insert(0, "true")
        return render(request, 'courses/new_exam.html', context)
    else:
        return redirect('/')


def exam_detail(request, subject_id, exam_id):
    xm_id = save_exam_id
    sub = get_list_or_404(subject, subject_id=subject_id)
    xm = get_list_or_404(exams, exam_id=exam_id)
    context = {
        'sub': sub,
        'xm': xm,
        'subject_id': subject_id,
        'exam_id': exam_id,
    }
    render(request, 'courses/exam_detail.html', context)
    if session_teacher[0] == "true":
        homepage_teacher.insert(0, "true")
        return render(request, 'courses/exam_detail.html', context)
    else:
        return redirect('/')


def st_exam_detail(request, subject_id, exam_id):
    xm_id = save_exam_id
    sub = get_list_or_404(subject, subject_id=subject_id)
    xm = get_list_or_404(exams, exam_id=exam_id)
    print("user name:", uname)

    context = {
        'sub': sub,
        'xm': xm,
        'subject_id': subject_id,
        'exam_id': exam_id,
    }
    render(request, 'courses/st_exam_detail.html', context)
    if session_student[0] == "true":
        homepage_student.insert(0, "true")
        return render(request, 'courses/st_exam_detail.html', context)
    else:
        return redirect('/')


def take_exam(request, subject_id, exam_id):

    xm_id = save_exam_id
    sub = get_list_or_404(subject, subject_id=subject_id)
    xm = get_list_or_404(exams, exam_id=exam_id)
    ques_set = get_list_or_404(question_set, exam_id=exam_id)
    global uname
    # get questions
    ques = get_list_or_404(question, set_id_id=ques_set[0].set_id)
    # q_set_id = ques_set[0].set_id
    # get standard answers
    ans1 = get_list_or_404(answer, question_id_id=ques[0].question_id)
    ans2 = get_list_or_404(answer, question_id_id=ques[1].question_id)
    standard_answer1 = ans1[0].answer_text
    standard_answer2 = ans2[0].answer_text

    # global uname
    user_name = uname
    usr = get_list_or_404(user, username=user_name)
    uid = usr[0].user_id
    # ger response texts
    if request.method == 'POST':
        res_text1 = request.POST['res_text1']
        res_text2 = request.POST['res_text2']
        # create response obj

        resp = response.objects.create(
            question_id_id=ques[0].question_id, user_id_id=uid, response_text=res_text1)

        resp.save()
        resp2 = response.objects.create(
            question_id_id=ques[1].question_id, user_id_id=uid, response_text=res_text2)

        resp2.save()

        s1, s2 = leven.preprocess(standard_answer1, res_text1)
        similarity_score = leven.levenshtein_similarity(s1, s2)

        # print("The similarity of question" ":", similarity_score)
        score_answer = 10*similarity_score
        jw_similarity = jaro.jaro_winkler(s1, s2)
        score_answer_jw = 10*jw_similarity

        # ------ jaccard------
        inp = standard_answer1
        inp1 = res_text1

        # tokenizing and remove stopword from Standard Answer
        tokens = word_tokenize(inp.lower())
        tokens = [
            token for token in tokens if token not in string.punctuation]
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        processed_text = ' '.join(tokens)
        tokens1 = word_tokenize(inp1.lower())
        tokens1 = [
            token for token in tokens1 if token not in string.punctuation]
        stop_words1 = set(stopwords.words('english'))
        tokens1 = [
            token for token in tokens1 if token not in stop_words]
        processed_text1 = ' '.join(tokens1)

        vectorizer = TfidfVectorizer()

        tfidf_matrix = vectorizer.fit_transform(
            [processed_text, processed_text1])

        # Calculate the Jaccard similarity
        jaccard_distance1 = jaccard.jaccard_similarity(
            tfidf_matrix[0].toarray().flatten(), tfidf_matrix[1].toarray().flatten())

        jaccard_sim1 = 1 - jaccard_distance1
        jac_scr1 = jaccard_sim1 * 10

        # --------- hamming---

        hamming_distance = hamming(tfidf_matrix[0].toarray(
        ).flatten(), tfidf_matrix[1].toarray().flatten())
        hamming_score1 = 1 - hamming_distance

        # -------- end hamming
        # cosine ---
        cos_distance = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

        # Calculate the similarity score
        cos_score1 = cos_distance

        cm_scr1 = max(score_answer, score_answer_jw)
        # save score
        save_scr1 = score.objects.create(
            question_id_id=ques[0].question_id, user_id_id=uid, score=score_answer)
        save_scr1.save()

        # send the score to template
        # answer = {
        #     'score': score_answer
        # }
        # get similarity for question

        # ----------------2 ----------------
        s1, s2 = leven.preprocess(standard_answer2, res_text2)
        similarity_score = leven.levenshtein_similarity(s1, s2)

        # print("The similarity of question", i+1, ":", similarity_score)
        score_answer1 = 10*similarity_score
        jw_similarity = jaro.jaro_winkler(s1, s2)
        score_answer_jw2 = 10*jw_similarity

        # jaccard
        inp = standard_answer2
        inp1 = res_text2

        # tokenizing and remove stopword from Standard Answer
        tokens = word_tokenize(inp.lower())
        tokens = [
            token for token in tokens if token not in string.punctuation]
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words]
        processed_text = ' '.join(tokens)
        tokens1 = word_tokenize(inp1.lower())
        tokens1 = [
            token for token in tokens1 if token not in string.punctuation]
        stop_words1 = set(stopwords.words('english'))
        tokens1 = [
            token for token in tokens1 if token not in stop_words]
        processed_text1 = ' '.join(tokens1)

        vectorizer = TfidfVectorizer()

        tfidf_matrix = vectorizer.fit_transform(
            [processed_text, processed_text1])

        # Calculate the Jaccard similarity
        jaccard_distance2 = jaccard.jaccard_similarity(
            tfidf_matrix[0].toarray().flatten(), tfidf_matrix[1].toarray().flatten())

        jaccard_sim2 = 1 - jaccard_distance2
        jac_scr2 = jaccard_sim2 * 10
        # end jaccard
        # hamming
        hamming_distance = hamming(tfidf_matrix[0].toarray(
        ).flatten(), tfidf_matrix[1].toarray().flatten())
        hamming_score2 = 1 - hamming_distance

        # cosine ---
        cos_distance = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

        # Calculate the similarity score
        cos_score2 = cos_distance

        # choosen score 2 of all algos
        cm_scr2 = max(score_answer1, score_answer_jw2)
        save_scr2 = score.objects.create(
            question_id_id=ques[0].question_id, user_id_id=uid, score=score_answer1)
        save_scr2.save()
        print("score:", score_answer)
        total = cm_scr1+cm_scr2
        total = math.ceil(total)
        answer1 = {
            'score': score_answer,
            'score2': score_answer1,
            'jw1': score_answer_jw,
            'jw2': score_answer_jw2,
            'total_value': total,
        }
        return render(request, 'login/result.html', answer1)
    context = {
        'sub': sub,
        'xm': xm,
        'subject_id': subject_id,
        'exam_id': exam_id,
        'ques_set': ques_set,
        'ques': ques,
        'user_name': user_name
        # 'q_set_id': q_set_id,
    }
    # render(request, 'courses/take_exam.html', context)
    if session_student[0] == "true":
        homepage_student.insert(0, "true")
        return render(request, 'courses/take_exam.html', context)
    else:
        return redirect('/')
    # return render(request, 'answer.html', question)

    # save_exam_id(exam_id)
    # redirect to a success page
    # return redirect('login:create_set', subject_id=subject_id, exam_id=exam_id)
    # return redirect('exhibition:map', lat=48.128365, lng=11.5662713, zoom=3)


def create_set(request, subject_id, exam_id):
    sub = get_list_or_404(subject, subject_id=subject_id)
    xm = get_list_or_404(exams, exam_id=exam_id)
    context = {
        'sub': sub,
        'xm': xm,
        'subject_id': subject_id,
        'exam_id': exam_id,
    }
    if request.method == 'POST':
        set_id = request.POST['set_id']
        set_number = request.POST['set_number']
        ques_set = question_set.objects.create(subject_id_id=subject_id,
                                               exam_id_id=exam_id, set_id=set_id, set_number=set_number)
        ques_set.save()
        # redirect to a success page
        return redirect('login:course_detail', subject_id=subject_id)

    if session_teacher[0] == "true":
        homepage_teacher.insert(0, "true")
        return render(request, 'courses/create_set.html', context)
    else:
        return redirect('/')


# text similarity views
# def similarity(request):


def teacher_result(request, subject_id, exam_id):
    global uname

    usr = get_list_or_404(user)

    xm = get_list_or_404(exams, exam_id=exam_id)
    xm_id = xm[0].exam_id
    scr = get_list_or_404(score)

    context = {
        'usr': usr,
        'xm_id': xm_id,
        'scr': scr
    }
    return render(request, 'courses/t_result.html', context)


def st_result(request, subject_id, exam_id):
    scores = score.objects.all()
    context = {
        'scores': scores
    }
    return render(request, 'course/st_result.html', context)


def logout_user(request):
    session_teacher.insert(0, "false")
    session_student.insert(0, "false")
    homepage_teacher.insert(0, "false")
    homepage_student.insert(0, "false")
    return redirect('/')
