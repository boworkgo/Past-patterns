import random
import re
import sqlite3
from collections import defaultdict
from datetime import datetime
from functools import reduce

import matplotlib.pyplot as plt
import numpy as np
from django import forms
from django.forms import Textarea
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic

import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from pandas.io import sql

from .models import Event


class IndexView(generic.ListView):
    template_name = "posts/index.html"
    context_object_name = "latest_posts"

    def get_queryset(self):
        return Event.objects.all()[:10]


class HistoryView(generic.DetailView):
    model = Event
    template_name = "posts/history.html"
    context_object_name = "post"


class CreateView(generic.edit.CreateView):
    model = Event
    fields = ["title", "text"]
    exclude = ["pub_date"]
    widgets = {"text": Textarea(attrs={"cols": 100, "rows": 15})}
    template_name = "posts/create.html"

    def get_success_url(self):
        return reverse("posts:index")


class Graph:
    def __init__(self, n):
        self.number_edges = n
        self.visited = [False] * n
        self.adj = defaultdict(list)
        self.connections = []

    def add_edge(self, n1, n2):
        self.adj[n1].append(n2)
        self.adj[n2].append(n1)

    def dfs(self):
        for i in range(self.number_edges):
            if not self.visited[i]:
                self.connections.append([])
                self.traverse_adj(i)

    def traverse_adj(self, i):
        self.connections[len(self.connections) - 1].append(i)
        self.visited[i] = True
        for j in self.adj[i]:
            if not self.visited[j]:
                self.traverse_adj(j)


class EventAnalysis:
    def __init__(self):
        conn = sqlite3.connect("db.sqlite3")
        self.data = sql.read_sql("SELECT * FROM posts_event;", con=conn)
        conn.close()
        self.clean_data()
        self.feature_engineering()
        self.generate_visuals()

    def string_clean(self, s):
        s = re.sub("[^a-zA-Z ]+", "", s).lower()
        s = re.sub(" +", " ", s).strip().split(" ")
        stop_words = set(stopwords.words("english"))
        s = [w for w in s if not w in stop_words]
        ps = PorterStemmer()
        s = list(set([ps.stem(w) for w in s]))
        return s

    def clean_data(self):
        self.data["cleansed_title"] = self.data["title"].map(self.string_clean)
        self.data["cleansed_text"] = self.data["text"].map(self.string_clean)

    def calculate_hours(self, time1, time2):
        def difference(idx1, idx2):
            return int(time2[idx1:idx2]) - int(time1[idx1:idx2])

        year = difference(0, 4)
        month = difference(5, 7)
        day = difference(8, 10)
        hour = difference(11, 13)
        minute = difference(14, 16)
        return year * 365 * 24 + month * 30 * 24 + day * 24 + hour + minute / 60

    def feature_engineering(self):
        time_spent, day_id = [1], []
        anchor_day, day_i = self.data["pub_date"][0][:10], 1
        for i in range(self.data.shape[0]):
            if i != 0:
                time_spent.append(
                    self.calculate_hours(
                        self.data["pub_date"][i - 1], self.data["pub_date"][i]
                    )
                )
            if self.data["pub_date"][i][:10] != anchor_day:
                day_i += 1
                anchor_day = self.data["pub_date"][i][:10]
            day_id.append(day_i)
        self.last_day_id = day_i
        self.data["time_spent"] = time_spent
        self.data["day_id"] = day_id
        self.data["is_important"] = self.data["title"].map(lambda x: x != "*")

        connected_components = Graph(len(self.data["id"]))
        added_edges = set()
        for i, title in enumerate(self.data["cleansed_title"]):
            for j, other in enumerate(self.data["cleansed_title"]):
                if (
                    i != j
                    and set(title) & set(other)
                    and frozenset({i, j}) not in added_edges
                ):
                    connected_components.add_edge(i, j)
                    added_edges.add(frozenset({i, j}))
        connected_components.dfs()
        group_number = 1
        id_group = dict()
        for group in connected_components.connections:
            for n in group:
                id_group[n] = group_number
            group_number += 1
        self.last_group_number = group_number
        self.data["group_id"] = [id_group[i] for i in range(self.data.shape[0])]
        self.data["pub_date_datetime"] = pd.to_datetime(
            self.data["pub_date"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        )
        time = pd.DataFrame(self.data[["pub_date_datetime", "time_spent"]])
        time = time.set_index(["pub_date_datetime"])
        time = time.resample("D").mean()
        self.time_df = time

    def past_day_pie(self):
        past_day = self.data[self.data.day_id == self.last_day_id]
        return past_day["time_spent"], past_day["title"]

    def grouping_pie(self):
        group_hours, group_words = [], []
        for i in range(1, self.last_group_number):
            group = self.data[self.data.group_id == i]
            group_hours.append(sum(group["time_spent"]))
            words = reduce(lambda a, b: set(a) | set(b), group["cleansed_title"], [])
            group_words.append(
                "\n".join(
                    [
                        w
                        for w in set(
                            random.sample(words, 4 if 4 <= len(words) else len(words))
                        )
                    ]
                )
            )
        return (group_hours, group_words)

    def time_plot(self):
        return self.time_df

    def generate_visuals(self):
        self.past_day_pie()
        self.grouping_pie()
        self.time_plot()


e = EventAnalysis()

def analytics(request):
    if len(Event.objects.all()) > 0:
        print(e.data)
    return render(
        request, "posts/analytics.html", context={"events": Event.objects.all()}
    )


class DeleteView(generic.DeleteView):
    model = Event

    def get_success_url(self):
        return reverse("posts:index")

from chartjs.views.lines import BaseLineChartView

class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]

class GroupingPieChartJSONView(BaseLineChartView): # Come on, django-chartjs. Only line chart is supported?
    stats, labels = e.grouping_pie()
    
    def get_labels(self):
        return self.labels
    
    def get_providers(self):
        return ["first_set"]
    
    def get_data(self):
        return [self.stats]
    
    def get_context_data(self):
        context = {
            'data': {
                'labels': self.get_labels(),
                'datasets': self.get_datasets()
            }
        }
        return context