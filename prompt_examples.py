"""Example question/SQL pairs used by the few-shot prompting strategies.

Strategies come from https://arxiv.org/abs/2305.11853
  - single-domain: examples written against OUR database
  - cross-domain:  examples written against a DIFFERENT database (shown with its schema)
"""

# Question/SQL pairs for our own database (the youth orchestra).
SINGLE_DOMAIN_EXAMPLES = [
    {
        "question": "Who conducts each ensemble?",
        "sql": (
            "SELECT e.name AS ensemble, c.name AS conductor\n"
            "FROM ensemble e\n"
            "JOIN conductor c ON e.conductor_id = c.conductor_id;"
        ),
    },
    {
        "question": "Which players are in more than one ensemble?",
        "sql": (
            "SELECT p.first_name, p.last_name, COUNT(m.ensemble_id) AS ensemble_count\n"
            "FROM player p\n"
            "JOIN membership m ON p.player_id = m.player_id\n"
            "GROUP BY p.player_id\n"
            "HAVING COUNT(m.ensemble_id) > 1;"
        ),
    },
    {
        "question": "Who sits first chair in each section of the Jazz Band?",
        "sql": (
            "SELECT s.name AS section, p.first_name, p.last_name\n"
            "FROM membership m\n"
            "JOIN ensemble e ON m.ensemble_id = e.ensemble_id\n"
            "JOIN section s ON m.section_id = s.section_id\n"
            "JOIN player p ON m.player_id = p.player_id\n"
            "WHERE e.name = 'Jazz Band' AND m.chair_number = 1;"
        ),
    },
]

# A different database: the dog show example from the CS 452 class content.
CROSS_DOMAIN_SCHEMA = """create table person (
    person_id integer primary key,
    name varchar(20) not null
);

create table phone (
    phone_id integer primary key,
    person_id integer not null,
    area_code int not null,
    number int not null,
    can_recieve_sms tinyint not null,
    foreign key (person_id) references person (person_id)
);

create table dog (
    dog_id integer primary key,
    name varchar(35),
    breed varchar(35),
    birth_date date
);

create table award (
    award_id integer primary key,
    dog_id integer not null,
    event_date date,
    award_name varchar(25) not null,
    foreign key (dog_id) references dog (dog_id)
);

create table person_dog (
    dog_id integer,
    person_id integer,
    foreign key (dog_id) references dog (dog_id),
    foreign key (person_id) references person (person_id)
);"""

CROSS_DOMAIN_EXAMPLES = [
    {
        "question": "Which are the most awarded dogs?",
        "sql": (
            "SELECT d.name, COUNT(a.award_id) AS award_count\n"
            "FROM dog d\n"
            "JOIN award a ON d.dog_id = a.dog_id\n"
            "GROUP BY d.dog_id\n"
            "ORDER BY award_count DESC;"
        ),
    },
    {
        "question": "Which dogs have multiple owners?",
        "sql": (
            "SELECT d.dog_id, d.name\n"
            "FROM dog d\n"
            "JOIN person_dog pd ON d.dog_id = pd.dog_id\n"
            "GROUP BY d.dog_id\n"
            "HAVING COUNT(pd.person_id) > 1;"
        ),
    },
    {
        "question": "Who doesn't have a way for us to text them?",
        "sql": (
            "SELECT p.person_id, p.name\n"
            "FROM person p\n"
            "LEFT JOIN phone ph ON p.person_id = ph.person_id AND ph.can_recieve_sms = 1\n"
            "WHERE ph.phone_id IS NULL;"
        ),
    },
]
