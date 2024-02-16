Aplicación que lee un conjunto de capturas formadas por:

* video de aprox 1 minute
* buffer de ambos electrodos
* json para sincronizar video y buffer

# Para qué sirve

* contar las ebjas que salen por el escape y etiquetar el video
* Probar un algoritmos de conteo

	* Se le proporcionan los buffers de los electrodos y
	* Recibe un Json con el número de abejas y en qué instante del video los ha encontrado
	* el algoritmo debe estar en recurso web estandarizado (POST)
	* Devolver también el tiempo que tarda en realizarse
