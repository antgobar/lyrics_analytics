from lyrics_analytics.api.extensions import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class LyricsStats(db.Model):

    __tablename__ = "lyrics_stats"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    album = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    count = db.Column(db.Integer(), nullable=False)
    unique_count = db.Column(db.Integer(), nullable=False)
    uniqueness_score = db.Column(db.Float(precision=3), nullable=False)

    def __repr__(self):
        return f"<LyricsStats {self.name}, {self.title}, {self.count}>"
