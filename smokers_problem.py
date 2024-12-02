import threading
import random
import time


class SmokersSimulation:
    def __init__(self, iterations):
        # Semáforos para sincronización
        self.agent_semaphore = threading.Semaphore(0)
        self.smoker_semaphores = {
            'tabaco': threading.Semaphore(0),
            'papel': threading.Semaphore(0),
            'fósforos': threading.Semaphore(0)
        }
        self.mutex = threading.Lock()

        # Ingredientes disponibles
        self.ingredients = ['tabaco', 'papel', 'fósforos']
        self.current_ingredients = set()

        # Contador de iteraciones
        self.max_iterations = iterations
        self.current_iteration = 0
        self.simulation_complete = threading.Event()

    def agent(self):
        """Agente que provee ingredientes aleatoriamente"""
        while self.current_iteration < self.max_iterations:
            with self.mutex:
                # Seleccionar dos ingredientes al azar
                ingredient_pair = random.sample(self.ingredients, 2)
                self.current_ingredients = set(ingredient_pair)
                print(f"Iteración {self.current_iteration + 1} - Agente provee: {ingredient_pair}")

            # Despertar al fumador que puede fumar
            missing_ingredient = (set(self.ingredients) - set(ingredient_pair)).pop()
            self.smoker_semaphores[missing_ingredient].release()

            # Esperar a que el fumador termine
            self.agent_semaphore.acquire()

            # Incrementar iteración
            self.current_iteration += 1
            time.sleep(1)  # Simulación de tiempo entre rondas

        # Marcar simulación como completa
        self.simulation_complete.set()

    def smoker(self, ingredient):
        """Fumador con un ingrediente específico"""
        while not self.simulation_complete.is_set():
            # Esperar a ser despertado
            self.smoker_semaphores[ingredient].acquire()

            # Salir si la simulación ha terminado
            if self.simulation_complete.is_set():
                break

            with self.mutex:
                print(f"Fumador con {ingredient} puede fumar")
                self.current_ingredients.clear()

            # Fumar
            time.sleep(random.uniform(0.5, 1.5))
            print(f"Fumador con {ingredient} ha fumado")

            # Notificar al agente que ha terminado
            self.agent_semaphore.release()


def main():
    # Solicitar número de iteraciones al usuario
    while True:
        try:
            iterations = int(input("Ingrese el número de iteraciones para la simulación de fumadores: "))
            if iterations > 0:
                break
            else:
                print("Por favor, ingrese un número positivo.")
        except ValueError:
            print("Entrada inválida. Ingrese un número entero.")

    # Crear instancia de simulación con iteraciones especificadas
    simulation = SmokersSimulation(iterations)

    # Crear hilos para el agente y los fumadores
    agent_thread = threading.Thread(target=simulation.agent)
    smoker_threads = [
        threading.Thread(target=simulation.smoker, args=(ingredient,))
        for ingredient in simulation.ingredients
    ]

    # Iniciar hilos
    agent_thread.start()
    for thread in smoker_threads:
        thread.start()

    # Esperar a que todos los hilos terminen
    agent_thread.join()
    for thread in smoker_threads:
        thread.join()

    print(f"Simulación completada después de {iterations} iteraciones.")


if __name__ == "__main__":
    main()