import ollama
import time
from typing import List, Dict, Any

# Modelle und Zeitmessungen
# Modell: tinyllama
#   Durchlauf 1: 5.6682 Sekunden
#   Durchlauf 2: 0.8991 Sekunden
#   Verbesserung (2. vs. 1. Lauf): 84.14%
# Modell: llama3
#   Durchlauf 1: 11.0157 Sekunden
#   Durchlauf 2: 5.5730 Sekunden
#   Verbesserung (2. vs. 1. Lauf): 49.41%
# Modell: codellama
#   Durchlauf 1: 7.6754 Sekunden
#   Durchlauf 2: 8.2450 Sekunden
#   Verbesserung (2. vs. 1. Lauf): -7.42%
# Modell: gemma3:4b
#   Durchlauf 1: 10.4296 Sekunden
#   Durchlauf 2: 8.0742 Sekunden
#   Verbesserung (2. vs. 1. Lauf): 22.58%
# Modell: gemma3:12b-it-qat
#   Durchlauf 1: 60.7261 Sekunden
#   Durchlauf 2: 70.4627 Sekunden
#   Verbesserung (2. vs. 1. Lauf): -16.03%
# Modell: mistral
#   Durchlauf 1: 9.1980 Sekunden
#   Durchlauf 2: 1.8704 Sekunden
#   Verbesserung (2. vs. 1. Lauf): 79.67%
# Modell: phi4-mini
#   Durchlauf 1: 4.9981 Sekunden
#   Durchlauf 2: 4.0466 Sekunden
#   Verbesserung (2. vs. 1. Lauf): 19.04%
# Modell: phi4
#   Durchlauf 1: 44.3827 Sekunden
#   Durchlauf 2: 39.3803 Sekunden
#   Verbesserung (2. vs. 1. Lauf): 11.27%



def benchmark_ollama_models(
        model_names: List[str],
        prompt: str = 'Warum ist der Himmel blau?',
        num_runs_per_model: int = 2
) -> Dict[str, List[float]]:
    """
    Führt einen Benchmark für eine Liste von Ollama LLMs durch.
    Jedes Modell beantwortet eine Standardfrage mehrmals, um die Ladezeiten
    und nachfolgende Antwortzeiten zu messen.

    Args:
        model_names: Eine Liste von Modellnamen (z.B. ['llama3', 'mistral']).
        prompt: Die Frage, die an jedes Modell gestellt wird.
        num_runs_per_model: Wie oft die Frage pro Modell gestellt werden soll.

    Returns:
        Ein Dictionary, das für jeden Modellnamen eine Liste der benötigten Zeiten (in Sekunden) enthält.
    """
    results: Dict[str, List[float]] = {}

    for model_name in model_names:
        print(f"\n--- Teste Modell: {model_name} ---")
        model_times: List[float] = []

        for i in range(num_runs_per_model):
            print(f"  Anfrage {i + 1}/{num_runs_per_model} für {model_name}...")
            start_time = time.perf_counter()  # Genauere Zeitmessung

            try:
                response = ollama.chat(model=model_name, messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ])
                end_time = time.perf_counter()
                duration = end_time - start_time
                model_times.append(duration)

                print(f"    Antwort in {duration:.4f} Sekunden.")
                # Optional: Gib die Antwort aus, um zu prüfen, ob alles funktioniert
                # print(f"    Antwort: {response['message']['content'][:100]}...") # Nur die ersten 100 Zeichen

            except ollama.ResponseError as e:
                print(f"  Fehler bei der Kommunikation mit Modell {model_name}: {e}")
                print(
                    f"  Stellen Sie sicher, dass das Modell '{model_name}' mit 'ollama pull {model_name}' installiert ist.")
                model_times.append(float('inf'))  # Unendlich als Indikator für Fehler
                break  # Wenn ein Modell nicht gefunden wird, brechen wir für dieses ab
            except Exception as e:
                print(f"  Ein unerwarteter Fehler bei Modell {model_name} ist aufgetreten: {e}")
                model_times.append(float('inf'))
                break

        results[model_name] = model_times

    return results


if __name__ == "__main__":
    # Definiere die Modelle, die du testen möchtest.
    # WICHTIG: Stelle sicher, dass diese Modelle mit 'ollama pull <modellname>'
    # auf deinem System installiert sind!
    # gemma3:12b-it-qat ist ein Beispiel, verwende Modelle, die du hast.
    # Kleinere Modelle wie 'llama3' oder 'tinyllama' sind gut für erste Tests.
    test_models = ['tinyllama', 'llama3', 'codellama', 'gemma3:4b' , 'gemma3:12b-it-qat', 'mistral', 'phi4-mini', 'phi4']

    # Die Standardfrage
    test_prompt = 'Was ist der Sinn des Lebens?'

    print(f"Starte LLM-Benchmark mit {len(test_models)} Modellen und der Frage: '{test_prompt}'")

    benchmark_results = benchmark_ollama_models(
        model_names=test_models,
        prompt=test_prompt,
        num_runs_per_model=2  # Stelle die Frage 2x pro Modell
    )

    print("\n--- Benchmark Ergebnisse ---")
    for model, times in benchmark_results.items():
        print(f"Modell: {model}")
        if not times or all(t == float('inf') for t in times):
            print("  Fehler beim Ausführen oder Modell nicht gefunden.")
        else:
            for i, duration in enumerate(times):
                if duration == float('inf'):
                    print(f"  Durchlauf {i + 1}: Fehler")
                else:
                    print(f"  Durchlauf {i + 1}: {duration:.4f} Sekunden")
            if len(times) > 1 and all(t != float('inf') for t in times):
                # Berechne die prozentuale Verbesserung, falls möglich
                if times[0] > 0:
                    improvement = ((times[0] - times[1]) / times[0]) * 100
                    print(f"  Verbesserung (2. vs. 1. Lauf): {improvement:.2f}%")