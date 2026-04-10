async function getApiStatus() {
  const baseUrl =
    process.env.API_INTERNAL_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "http://api:8000";

  try {
    const [healthResponse, bootstrapResponse] = await Promise.all([
      fetch(`${baseUrl}/health`, {
        cache: "no-store",
      }),
      fetch(`${baseUrl}/v1/auth/bootstrap-status`, {
        cache: "no-store",
      }),
    ]);

    if (!healthResponse.ok || !bootstrapResponse.ok) {
      throw new Error("API response was not ok");
    }

    return {
      status: "ok",
      bootstrap: await bootstrapResponse.json(),
    };
  } catch {
    return {
      status: "offline",
      bootstrap: null,
      error: "API no disponible todavia",
    };
  }
}

export default async function Home() {
  const api = await getApiStatus();

  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">NutriCore</p>
        <h1>Base operativa para consulta nutricional seria.</h1>
        <p className="lede">
          El starter ya fue adaptado para arrancar el producto: autenticacion,
          usuarios, persistencia inicial y una ruta clara para construir
          pacientes, evaluaciones y planes.
        </p>
      </section>

      <section className="grid">
        <article className="card">
          <h2>Fase actual</h2>
          <ul>
            <li>Login JWT y endpoints protegidos</li>
            <li>Pacientes, expediente, consultas y mediciones</li>
            <li>Evaluaciones versionadas con GET base para adultos</li>
          </ul>
        </article>

        <article className="card accent">
          <h2>Siguiente bloque</h2>
          <ul>
            <li>Estrategia nutricional sobre resultados calculados</li>
            <li>Distribucion diaria y estructura del plan</li>
            <li>Editor de plan y salida PDF</li>
          </ul>
        </article>

        <article className="card">
          <h2>Estado de API</h2>
          <pre>{JSON.stringify(api, null, 2)}</pre>
        </article>
      </section>

      <section className="footer-note">
        <p>
          Dashboard actual disponible en <a href="/patients">/patients</a> para
          listar pacientes, revisar consultas y ejecutar evaluaciones con JWT.
        </p>
      </section>

      <section className="footer-note">
        <p>
          Primer acceso esperado: usa el admin bootstrap definido en `.env` para
          autenticarte contra `POST /v1/auth/login`.
        </p>
      </section>
    </main>
  );
}
