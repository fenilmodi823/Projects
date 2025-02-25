#ifdef GL_ES
precision mediump float;
#endif

#define PI 3.1415926538

// Uniforms from JavaScript
uniform vec2 iResolution;
uniform float iTime;
uniform sampler2D iChannel0;
uniform sampler2D iChannel1;

// Wormhole and camera settings (constants)
const float a = 2.3;
const float N = -1.0;
const float dt = -1.0;
const int maxSteps = 1000;

const float camL = 5.0;  // camera distance
const float zoom = 1.5;  // camera zoom

// Wormhole function r(l)
float Ltor(float l) {
    float kappa = max(0.0, 2.0 * (abs(l) - a) / (PI * N));
    return a * a * tan(kappa) - 0.5 * log(1.0 + kappa * kappa);
}

// Wormhole derivative
float LtoDR(float l) {
    float x = max(0.0, 2.0 * (abs(l) - a) / (PI * N));
    return a / (1.0 + x * x);
}

// Main image function
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Ray projection
    vec2 uv = (2.0 * fragCoord - iResolution) / iResolution.x;
    // Construct a 3D direction: note that we use uv.x and uv.y as the y and z components.
    vec3 vel = normalize(vec3(-zoom, uv.x, uv.y));
    // beta is the normalized 2D component (from uv) – used later if needed
    vec2 beta = normalize(uv);

    // Initialize ray parameters
    float l = camL;
    float r = Ltor(l);
    float dl = vel.x;
    float H = length(uv);
    float phi = 0.0;
    float dr = 0.0;

    int steps = 0;
    // Ray tracing loop
    while (abs(l) < max(abs(camL) * 2.0, a + 2.0) && steps < maxSteps) {
        dr = LtoDR(l);
        r = Ltor(l);

        float dx = dl * dr * cos(phi) - H / r * sin(phi);
        float dy = dl * dr * sin(phi) + H / r * cos(phi);

        // Update ray parameters
        l += dl * dt;
        phi += H / r * dt;
        dl += (H * H * dr) / (r * r) * dt;

        steps++;
    }
    
    // Compute a “sky” direction based on the final ray parameters
    float dx_final = dl * dr * cos(phi) - H / r * sin(phi);
    float dy_final = dl * dr * sin(phi) + H / r * cos(phi);
    vec3 cubeVec = vec3(-dx_final, 0.0, -dy_final);

    // Sample from one of the textures based on the ray result.
    // (Here we use the x and y components of cubeVec as texture coordinates.)
    if (l > 0.0) {
        fragColor = texture2D(iChannel0, cubeVec.xy);
    } else {
        fragColor = texture2D(iChannel1, cubeVec.xy);
    }
}

void main() {
  mainImage(gl_FragColor, gl_FragCoord.xy);
}
