#version 330

// Passed in from vertex shader
in VertexData
{
	vec3 v2f_viewSpaceNormal;
	vec3 v2f_viewSpacePosition;
	vec2 v2f_texCoord;
};

out vec4 fragmentColor;

// Textures
uniform sampler2D diffuseTexture;

void main()
{
    // Load from texture - no lighting
    vec3 baseDiffuse = texture(diffuseTexture, v2f_texCoord).xyz;
    fragmentColor = vec4(baseDiffuse, 1.0);
}