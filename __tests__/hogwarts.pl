muggle(X) :-
    not(wizard(X)),
    \+ witch(X).

wizard(X) :-
    guy(X),
    magical(X).

witch(X) :-
    girl(X),
    magical(X).

has_wand(X) :- magical(X).

girl(hermione).
guy(harry).
guy(ron).
guy(dudley).

magical(hermione).
magical(harry).
magical(ron).
