import MetaTrader5 as mt5

# Define el término o activo que deseas buscar (ej. "HBAR", "BTC", "USD")
TERMINO_BUSQUEDA = "HBAR"

if mt5.initialize():
    simbolos = mt5.symbols_get()
    print(f"\n--- SÍMBOLOS DISPONIBLES QUE COINCIDEN CON '{TERMINO_BUSQUEDA}' ---")
    
    if simbolos:
        encontrados = 0
        termino_upper = TERMINO_BUSQUEDA.upper()
        
        for s in simbolos:
            nombre = s.name.upper()
            desc = s.description.upper()
            
            if termino_upper in nombre or termino_upper in desc:
                print(f"Nombre exacto: '{s.name}' | Descripción: {s.description} | Ruta: {s.path}")
                encontrados += 1
                
        if encontrados == 0:
            print(f"No se encontraron símbolos relacionados con '{TERMINO_BUSQUEDA}'.")
    else:
        print("No se pudieron recuperar los símbolos desde la terminal.")
        
    mt5.shutdown()
else:
    print("Error al conectar con MetaTrader 5. Verifica que la aplicación esté abierta.")