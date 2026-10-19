from django.db.models import Value
from django.db.models.functions import Concat
from rest_framework import serializers

from cinema.models import Movie, Actor, Genre, CinemaHall, MovieSession, Order, Ticket


class ActorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = Actor
        fields = ["id", "first_name", "last_name", "full_name"]
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class CinemaHallSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(read_only=True)
    class Meta:
        model = CinemaHall
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    actors = serializers.SerializerMethodField()

    actors_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
    )

    actor_ids = serializers.PrimaryKeyRelatedField(
        queryset=Actor.objects.all(),
        many=True,
        write_only=True,
        source="actors",
        required=False,
    )

    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        write_only=True,
        source="genres",
        required=False,
    )

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "duration",
            "genres",
            "actors",
            "actor_ids",
            "genre_ids",
            "actors_data",
        ]

    def get_genres(self, obj):
        return list(obj.genres.values_list("name", flat=True))

    def get_actors(self, obj):
        return [
            f"{actor.first_name} {actor.last_name}"
            for actor in obj.actors.all()
        ]

    def create(self, validated_data):
        actors = validated_data.pop("actors", [])
        genres = validated_data.pop("genres", [])
        validated_data.pop("actors_data", [])

        movie = Movie.objects.create(**validated_data)
        movie.actors.set(actors)
        movie.genres.set(genres)

        return movie


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "description", "duration", "genres", "actors"]


class MovieSessionListSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    cinema_hall_name = serializers.CharField(source="cinema_hall.name", read_only=True)
    cinema_hall_capacity = serializers.IntegerField(source="cinema_hall.capacity", read_only=True)

    class Meta:
        model = MovieSession
        fields = ["id", "show_time", "movie_title", "cinema_hall_name", "cinema_hall_capacity"]


class MovieSessionDetailSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    cinema_hall = CinemaHallSerializer(read_only=True)

    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source="movie",
        write_only=True,
    )
    cinema_hall_id = serializers.PrimaryKeyRelatedField(
        queryset=CinemaHall.objects.all(),
        source="cinema_hall",
        write_only=True,
    )

    class Meta:
        model = MovieSession
        fields = [
            "id",
            "show_time",
        ]


class MovieSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieSession
        fields = ["id", "show_time", "movie", "cinema_hall"]
