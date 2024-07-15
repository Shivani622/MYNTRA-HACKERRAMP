import React, { useState } from 'react';
import axios from 'axios';
import { Button, TextField, Container, Typography, Card, CardContent, CardMedia } from '@mui/material'; 
const ProductRecommendation = () => {
    const [inputSentence, setInputSentence] = useState('');
    const [product, setProduct] = useState(null);

    const handleRecommend = async () => {
        try {
            const response = await axios.post('http://localhost:5000/recommend', { input_sentence: inputSentence });
            setProduct(response.data);
        } catch (error) {
            console.error('Error fetching recommendation:', error);
        }
    };

    return (
        <Container>
            <Typography variant="h4" gutterBottom>Product Recommendation System</Typography>
            <TextField
                label="Describe the product you're looking for"
                variant="outlined"
                fullWidth
                value={inputSentence}
                onChange={(e) => setInputSentence(e.target.value)}
            />
            <Button variant="contained" color="primary" onClick={handleRecommend} style={{ marginTop: '20px' }}>
                Get Recommendation
            </Button>

            {product && (
                <Card style={{ marginTop: '20px' }}>
                    <CardMedia
                        component="img"
                        alt={product.product_name}
                        height="140"
                        image={product.product_description} 
                        title={product.product_name}
                    />
                    <CardContent>
                        <Typography gutterBottom variant="h5" component="div">
                            {product.product_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Product ID: {product.product_id}
                        </Typography>
                    </CardContent>
                </Card>
            )}
        </Container>
    );
};

export default ProductRecommendation;
