// Get the canvas and initialize the WebGL context
const canvas = document.getElementById("glCanvas");
const gl = canvas.getContext("webgl");
if (!gl) {
  console.error("WebGL not supported!");
}

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);

// Utility function to compile a shader
function loadShader(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.error("Shader compile error:", gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    return null;
  }
  return shader;
}

// Utility function to initialize a shader program
function initShaderProgram(gl, vsSource, fsSource) {
  const vertexShader = loadShader(gl, gl.VERTEX_SHADER, vsSource);
  const fragmentShader = loadShader(gl, gl.FRAGMENT_SHADER, fsSource);

  const shaderProgram = gl.createProgram();
  gl.attachShader(shaderProgram, vertexShader);
  gl.attachShader(shaderProgram, fragmentShader);
  gl.linkProgram(shaderProgram);
  if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
    console.error(
      "Unable to initialize the shader program:",
      gl.getProgramInfoLog(shaderProgram)
    );
    return null;
  }
  return shaderProgram;
}

// Vertex shader code: a simple pass-through shader for a fullscreen quad
const vsSource = `
  attribute vec4 aVertexPosition;
  void main() {
    gl_Position = aVertexPosition;
  }
`;

// Create a fullscreen quad (two triangles covering the viewport)
const positions = [-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0];
const positionBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);

// Create two dummy 1x1 textures for iChannel0 and iChannel1
function createDummyTexture(gl, colorArray) {
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  // 1x1 pixel, RGBA format
  const pixel = new Uint8Array(colorArray);
  gl.texImage2D(
    gl.TEXTURE_2D,
    0,
    gl.RGBA,
    1,
    1,
    0,
    gl.RGBA,
    gl.UNSIGNED_BYTE,
    pixel
  );
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  return texture;
}
const texture0 = createDummyTexture(gl, [255, 0, 0, 255]); // Red texture
const texture1 = createDummyTexture(gl, [0, 0, 255, 255]); // Blue texture

// Load the fragment shader from shader.frag
fetch("shader.frag")
  .then((response) => response.text())
  .then((fsSource) => {
    const shaderProgram = initShaderProgram(gl, vsSource, fsSource);
    const programInfo = {
      program: shaderProgram,
      attribLocations: {
        vertexPosition: gl.getAttribLocation(shaderProgram, "aVertexPosition"),
      },
      uniformLocations: {
        iResolution: gl.getUniformLocation(shaderProgram, "iResolution"),
        iTime: gl.getUniformLocation(shaderProgram, "iTime"),
        iChannel0: gl.getUniformLocation(shaderProgram, "iChannel0"),
        iChannel1: gl.getUniformLocation(shaderProgram, "iChannel1"),
      },
    };

    // Render loop
    function render(now) {
      now *= 0.001; // Convert to seconds
      gl.clearColor(0.0, 0.0, 0.0, 1.0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.useProgram(programInfo.program);

      // Set up the vertex attribute
      gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
      gl.enableVertexAttribArray(programInfo.attribLocations.vertexPosition);
      gl.vertexAttribPointer(
        programInfo.attribLocations.vertexPosition,
        2, // components per vertex (x, y)
        gl.FLOAT,
        false,
        0,
        0
      );

      // Set uniforms
      gl.uniform2f(
        programInfo.uniformLocations.iResolution,
        canvas.width,
        canvas.height
      );
      gl.uniform1f(programInfo.uniformLocations.iTime, now);

      // Bind dummy textures to texture units 0 and 1
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, texture0);
      gl.uniform1i(programInfo.uniformLocations.iChannel0, 0);

      gl.activeTexture(gl.TEXTURE1);
      gl.bindTexture(gl.TEXTURE_2D, texture1);
      gl.uniform1i(programInfo.uniformLocations.iChannel1, 1);

      // Draw the quad
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      requestAnimationFrame(render);
    }
    requestAnimationFrame(render);
  })
  .catch((err) => {
    console.error("Error loading shader.frag:", err);
  });
