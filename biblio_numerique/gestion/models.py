from django.db import models


class Auteur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    nationalite = models.CharField(max_length=100)
    date_naissance = models.DateField()

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Livre(models.Model):
    titre = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True)
    date_publication = models.DateField()
    nombre_pages = models.PositiveIntegerField()
    auteur = models.ForeignKey(Auteur, on_delete=models.CASCADE, related_name='livres')
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.titre


class Emprunt(models.Model):
    nom_lecteur = models.CharField(max_length=200)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='emprunts')
    date_emprunt = models.DateField()
    date_retour = models.DateField()

    def __str__(self):
        return f"{self.nom_lecteur} - {self.livre.titre}"
