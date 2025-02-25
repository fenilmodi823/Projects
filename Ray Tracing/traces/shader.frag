#ifdef GL_ES
precision mediump float;
#endif

#define PI 3.1415926538

uniform vec2 iResolution;
uniform float iTime;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;

const float a = 2.3;
const float N = -1.0;
const float dt = -1.0;
const int maxSteps = 1000;

const float camL = 5.0;
const float zoom = 1.5;

float Ltor(float l) {
    float kappa = max(0.0, 2.0 * (abs(l) - a) / (PI * N));
    return a * a * tan(kappa) - 0.5 * log(1.0 + kappa * kappa);
}

float LtoDR(float l) {
    float x = max(0.0, 2.0 * (abs(l) - a) / (PI * N));
    return a / (1.0 + x * x);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (2.0 * fragCoord - iResolution) / iResolution.x;
    vec3 vel = normalize(vec3(-zoom, uv.x, uv.y));
    vec2 beta = normalize(uv);

    float l = camL;
    float r = Ltor(l);
    float dl = vel.x;
    float H = length(uv);
    float phi = 0.0;
    float dr = 0.0;

    int steps = 0;
    while (abs(l) < max(abs(camL) * 2.0, a + 2.0) && steps < maxSteps) {
        dr = LtoDR(l);
        r = Ltor(l);

        float dx = dl * dr * cos(phi) - H / r * sin(phi);
        float dy = dl * dr * sin(phi) + H / r * cos(phi);

        l += dl * dt;
        phi += H / r * dt;
        dl += (H * H * dr) / (r * r) * dt;

        steps++;
    }
    
    float dx_final = dl * dr * cos(phi) - H / r * sin(phi);
    float dy_final = dl * dr * sin(phi) + H / r * cos(phi);
    vec3 cubeVec = vec3(-dx_final, 0.0, -dy_final);

    if (l > 0.0) {
        fragColor = texture2D(iChannel0, cubeVec.xy);
    } else {
        fragColor = texture2D(iChannel1, cubeVec.xy);
    }
}

void main() {
  mainImage(gl_FragColor, gl_FragCoord.xy);
}
