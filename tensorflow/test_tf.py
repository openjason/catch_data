#Example of TensorFlow libary
<<<<<<< HEAD

import tensorflow as tf

# first, create a TensorFlow constant
const = tf.constant(2.0, name="const")

# create TensorFlow variables
b = tf.Variable(2.0, name='b')
c = tf.Variable(1.0, name='c')


d = tf.add(b, c, name='d')
e = tf.add(c, const, name='e')
a = tf.multiply(d, e, name='a')

# setup the variable initialisation
init_op = tf.global_variables_initializer()


with tf.Session() as sess:
    # initialise the variables
    sess.run(init_op)
    # compute the output of the graph
    a_out = sess.run(a)
    print("Variable a is {}".format(a_out))

# create TensorFlow variables
b = tf.placeholder(tf.float32, [None, 1], name='b')

a_out = sess.run(a, feed_dict={b: np.arange(0, 10)[:, np.newaxis]})
=======
import tensorflow as tf

a = tf.placeholder(tf.float32)

b = tf.placeholder(tf.float32)

add = tf.add(a,b)

sess = tf.Session
bingding = {a:1.5,b:2.5}
c = sess.run(add,feed_dict = bingding)
print (c)
>>>>>>> 4da214c8ba1ccc3a9c46f48aec7c7ca994fb9aa0
