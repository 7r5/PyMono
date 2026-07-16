a1="Exodia 1/3, al juntar todas las partes de Exhodia, el prohibido, eres capaz de asesinar directamente al jugador que peor te caiga, basicamente eres dios por un turno, al morir heredas todas las propiedades aunque el dinero se ira al banco"
a2="Exodia 2/3, al juntar todas las partes de Exhodia, el prohibido, eres capaz de asesinar directamente al jugador que peor te caiga, basicamente eres dios por un turno, al morir heredas todas las propiedades aunque el dinero se ira al banco"
a3="Exodia 3/3, al juntar todas las partes de Exhodia, el prohibido, eres capaz de asesinar directamente al jugador que peor te caiga, basicamente eres dios por un turno, al morir heredas todas las propiedades aunque el dinero se ira al banco"


import hashlib
h1 = hashlib.sha256(a1.encode("utf-8")).hexdigest()[:8]
h2 = hashlib.sha256(a2.encode("utf-8")).hexdigest()[:8]
h3 = hashlib.sha256(a3.encode("utf-8")).hexdigest()[:8]
print(h1)
print(h2)
print(h3)